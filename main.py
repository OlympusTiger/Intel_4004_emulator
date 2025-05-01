from argparse import ArgumentParser
from memory import MemoryManager

parser = ArgumentParser()

parser.add_argument(
    "-f",
    "--file",
    help="file to read",
    type=str,
    default="programs/program.txt",
)

args = parser.parse_args()

print(args)

mem = MemoryManager()
mem.ROM[0].read_from_file(args.file)
