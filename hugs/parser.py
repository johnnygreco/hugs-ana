import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('tract', type=str, help='HSC tract')
    parser.add_argument('patch', type=str, help='HSC patch')
    args = parser.parse_args()
    return args
