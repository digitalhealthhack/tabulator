# Author: Hubert Matthews (hubert@oxyware.com)
# Licence: public domain

from math import sqrt

from PIL import Image
import png


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
        with open('colours.txt', 'w') as f:
            for i in range(0, len(avg)/4):
                f.write(str(avg[4*i]) + " " 
                        + str(avg[4*i+1]) + " " 
                        + str(avg[4*i+2]) + " "
                        + str(self.rms_calc(avg, 4*i)) + "\n")

        # select only red pixels to reduce blue background pixels
        r = avg[::4]

        # save pixels for debug and graphing
        with open('red.txt', 'w') as f:
            for i in r:
                f.write(str(i) + "\n")

        # find edges using a hardwired threshold value of 0.5
        edges = []
        for i in range(0, len(r)-1): 
            if (r[i] <= 0.5 and r[i+1] > 0.5) or (r[i] > 0.5 and r[i+1] <= 0.5):
                edges += [i]

        if len(edges) != 4:
            return

        def get_drop(x, y):
            widthOfControlStrip = y - x

            minInControlStrip = min(r[x:y])
            minControlPosn = r[x:y].index(minInControlStrip) + x
            controlStripHeight = r[y] - r[x]
            proportionIntoControlStrip = (float(minControlPosn) - x) / widthOfControlStrip
            calculatedValueAtMinPosn = r[x] + proportionIntoControlStrip * controlStripHeight

            return (calculatedValueAtMinPosn - minInControlStrip)


        control = get_drop(edges[0] + 5, edges[1] - 5)
        patient = get_drop(
            int(edges[2] + 0.50 * (edges[3] - edges[2])),
            int(edges[2] + 0.80 * (edges[3] - edges[2]))
        )

        ratio = float(patient) / control * 100

        return {
            'normalised_drop_percent': int(ratio),
            'level': int(ratio / 20.0),
        }

