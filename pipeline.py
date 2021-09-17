#!/usr/bin/env python
# coding: utf-8
"""
SPO training pipeline
"""

import argparse
import os
import time

import numpy as np
import pandas as pd
import torch

import spo
import utils
from train import train
from eval import eval

def pipeline(config):
    # shortest path
    if config.prob == "sp":
        print("Running experiments for shortest path prob:")
    # knapsack
    if config.prob == "ks":
        print("Running experiments for multi-dimensional knapsack prob:")
    # travelling salesman
    if config.prob == "tsp":
        print("Running experiments for traveling salesman prob:")
    print()
    # create table
    save_path = utils.getSavePath(config)
    if os.path.isfile(save_path):
        df = pd.read_csv(save_path)
    else:
        df = pd.DataFrame(columns=["True SPO", "Unamb SPO", "Elapsed", "Epochs"])
    # set random seed
    np.random.seed(config.seed)
    torch.manual_seed(config.seed)

    for i in range(config.expnum):
        config.seed = np.random.randint(999)
        print("===============================================================")
        print("Experiment {}:".format(i))
        print("===============================================================")
        # generate data
        data = utils.genData(config)
        if config.prob == "ks":
            config.wght, data = data[0], (data[1], data[2])
        print()
        # build model
        model = utils.buildModel(config)
        # build data loader
        trainset, testset = utils.buildDataSet(data, model, config)
        print()
        # train
        tick = time.time()
        res = train(trainset, testset, model, config)
        tock = time.time()
        elapsed = tock - tick
        print("Time elapsed: {:.4f} sec".format(elapsed))
        print()
        # evaluate
        truespo, unambspo = eval(testset, res, model, config)
        # save
        row = {"True SPO":truespo, "Unamb SPO":unambspo,
               "Elapsed":elapsed, "Epochs":config.epoch}
        df = df.append(row, ignore_index=True)
        df.to_csv(save_path, index=False)
        print("Saved to " + save_path + ".")
        print("\n\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    # experiments configuration
    parser.add_argument("--mthd",
                        type=str,
                        default="spo",
                        choices=["2s", "spo", "bb"],
                        help="method")
    parser.add_argument("--seed",
                        type=int,
                        default=135,
                        help="random seed")
    parser.add_argument("--expnum",
                        type=int,
                        default=10,
                        help="number of experiments")
    parser.add_argument("--rel",
                        action="store_true",
                        help="train with relaxation model")
    parser.add_argument("--pred",
                        type=str,
                        default="lr",
                        choices=["lr", "rf"],
                        help="predictor of two-stage predict then optimize")
    parser.add_argument("--elog",
                        type=int,
                        default=0,
                        help="steps of evluation and log")
    parser.add_argument("--form",
                        type=str,
                        default="gg",
                        choices=["gg", "dfj", "mtz"],
                        help="TSP formulation")
    parser.add_argument("--path",
                        type=str,
                        default="./res",
                        help="path to save result")

    # solver configuration
    parser.add_argument("--lan",
                        type=str,
                        default="gurobi",
                        choices=["gurobi", "pyomo"],
                        help="modeling language")
    parser.add_argument("--solver",
                        type=str,
                        default="gurobi",
                        help="solver for Pyomo")

    # data configuration
    parser.add_argument("--data",
                        type=int,
                        default=1000,
                        help="training data size")
    parser.add_argument("--feat",
                        type=int,
                        default=5,
                        help="feature size")
    parser.add_argument("--deg",
                        type=int,
                        default=1,
                        help="features polynomial degree")
    parser.add_argument("--noise",
                        type=float,
                        default=0,
                        help="noise half-width")

    # optimization model configuration
    parser.add_argument("--prob",
                        type=str,
                        default="sp",
                        choices=["sp", "ks", "tsp"],
                        help="problem type")
    # shortest path
    parser.add_argument("--grid",
                        type=int,
                        nargs=2,
                        default=(20,20),
                        help="network grid for shortest path")
    # knapsack
    parser.add_argument("--items",
                        type=int,
                        default=48,
                        help="number of items for knapsack")
    parser.add_argument("--dim",
                        type=int,
                        default=3,
                        help="dimension for knapsack")
    parser.add_argument("--cap",
                        type=int,
                        default=30,
                        help="dimension for knapsack")
    # tsp
    parser.add_argument("--nodes",
                        type=int,
                        default=20,
                        help="number of nodes")

    # training configuration
    parser.add_argument("--batch",
                        type=int,
                        default=32,
                        help="batch size")
    parser.add_argument("--epoch",
                        type=int,
                        default=100,
                        help="number of epochs")
    parser.add_argument("--net",
                        type=int,
                        nargs='*',
                        default=[],
                        help="size of neural network hidden layers")
    parser.add_argument("--optm",
                        type=str,
                        default="adam",
                        choices=["sgd", "adam"],
                        help="optimizer neural network")
    parser.add_argument("--lr",
                        type=float,
                        default=1e-3,
                        help="learning rate")
    parser.add_argument("--l1",
                        type=float,
                        default=0,
                        help="l1 regularization parameter")
    parser.add_argument("--l2",
                        type=float,
                        default=0,
                        help="l2 regularization parameter")
    parser.add_argument("--smth",
                        type=float,
                        default=10,
                        help="smoothing parameter for Black-Box")
    parser.add_argument("--proc",
                        type=int,
                        default=1,
                        help="number of processor for optimization")

    # get configuration
    config = parser.parse_args()

    # run experiment pipeline
    pipeline(config)
