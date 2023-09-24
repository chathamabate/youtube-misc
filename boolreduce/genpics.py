
import os

dirname = os.path.dirname(__file__)

graphsdir = os.path.join(dirname, "./graphs")
picsdir = os.path.join(dirname, "./pics")

for filename in os.listdir(graphsdir):
    if filename.endswith(".gv"):
        absfile = os.path.join(graphsdir, filename)

        picname = filename[:-3] + ".svg"
        abspic = os.path.join(picsdir, picname)

        os.system(f"dot -Tsvg {absfile} -o {abspic}")


