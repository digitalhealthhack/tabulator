# Author: Hubert Matthews (hubert@oxyware.com)
# Licence: public domain

from math import sqrt
import png
from PIL import Image


class ScanImage(object):
    def rms_calc(self, a, i):
        return sqrt((a[i]*a[i] + a[i+1]*a[i+1] + a[i+2]*a[i+2])/3)

    def process(self):
        im = Image.open('tmp.png')
        x = im.rotate(180-87)
        x = x.crop((200, 545, 900, 620))
        x.save('tmp.png')

        rdr = png.Reader(filename='tmp.png')

        # get pixels as floats in [[RGB RGB RGB],[RGB...]] format
        pixels = rdr.asFloat()

        # average all pixels across all rows
        avg = [sum(s) for s in zip(*pixels[2])]

        # normalise the average
        avg = [i/pixels[1] for i in avg]

        # save all RGB components and grey levels
        f = open('colours.txt', 'w')
        for i in range(0, len(avg)/4):
            f.write(str(avg[4*i]) + " " 
                    + str(avg[4*i+1]) + " " 
                    + str(avg[4*i+2]) + " "
                    + str(self.rms_calc(avg, 4*i)) + "\n")
        f.close()

        # select only red pixels to reduce blue background pixels
        r = avg[::4]

        # save pixels for debug and graphing
        f = open('red.txt', 'w')
        for i in r:
            f.write(str(i) + "\n")
        f.close()

        # find edges using a hardwired threshold value of 0.5
        edges = []
        for i in range(0, len(r)-1): 
            if (r[i] <= 0.5 and r[i+1] > 0.5) or (r[i] > 0.5 and r[i+1] <= 0.5):
                edges += [i]

	print(edges)
        if len(edges) != 4:
            return

        def get_drop(x, y):
            print('x: {}'.format(x))
            print('y: {}'.format(y))

            print('r[x]: {}'.format(r[x]))
            print('r[y]: {}'.format(r[y]))



            widthOfControlStrip = y - x

            minInControlStrip = min(r[x:y])
            print('min: {}'.format(minInControlStrip))

            minControlPosn = r[x:y].index(minInControlStrip) + x
            print('min position {}'.format(minControlPosn))

            controlStripHeight = r[y] - r[x]
            print('height: {}'.format(controlStripHeight))

            proportionIntoControlStrip = (float(minControlPosn) - x) / widthOfControlStrip
            print('proportion strip: {}'.format(proportionIntoControlStrip))

            calculatedValueAtMinPosn = r[x] + proportionIntoControlStrip * controlStripHeight
            print('value at min pos: {}'.format(calculatedValueAtMinPosn))

            return (calculatedValueAtMinPosn - minInControlStrip)


        control = get_drop(edges[0] + 5, edges[1] - 5)
        #patient = get_drop(edges[2], edges[3])
        print()
        patient = get_drop(
            int(edges[2] + 0.50 * (edges[3] - edges[2])),
            int(edges[2] + 0.80 * (edges[3] - edges[2]))
        )

        widthOfPatientStrip = edges[3] - edges[2]
        #avgOfPatientStrip = sum(r[edges[2]:edges[3]]) / widthOfPatientStrip
        
        ## assume active portion of patient strip is from 45% to 55% of strip
        #lowerPercent = 0.45
        #upperPercent = 0.55
        #lowerEdge = int(edges[2] + lowerPercent * widthOfPatientStrip)
        #upperEdge = int(edges[2] + upperPercent * widthOfPatientStrip)
        #activeAvg = sum(r[lowerEdge:upperEdge]) / (upperEdge - lowerEdge)
        #activeDrop = (avgOfPatientStrip - activeAvg) / avgOfPatientStrip
        #normalisedDropPercent = activeDrop * 100.0 / controlDrop

        ratio = float(patient) / control * 100

        print('Normalised drop percent = ' + str(ratio))
        print("Level = " + str(int(ratio / 20.0)))


        return {
            'normalised_drop_percent': ratio,
            'level': int(ratio / 20.0),
        }

