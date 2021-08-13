#!/usr/bin/env python
# coding: utf-8

import gurobipy as gp
from gurobipy import GRB
from spo.model import optModel

class optGRBModel(optModel):
    """
    This is an abstract class for Gurobi-based optimization model
    """

    def setObj(self, c):
        """
        A method to set objective function

        Args:
            c (ndarray): cost of objective function
        """
        assert len(c) == self.num_cost, 'Size of cost vector cannot match vars.'
        obj = gp.quicksum(c[i] * self.x[k] for i, k in enumerate(self.x))
        self._model.setObjective(obj)

    def solve(self):
        """
        A method to solve model

        Returns:
            tuple: optimal solution (list) and objective value (float)
        """
        self._model.update()
        self._model.optimize()
        return [self.x[k].x for k in self.x], self._model.objVal

    def copy(self):
        """
        A method to copy model

        Returns:
            optModel: new copied model
        """
        new_model = super().copy()
        # update model
        self._model.update()
        # new model
        new_model._model = self._model.copy()
        # variables for new model
        x = new_model._model.getVars()
        new_model.x = {key: x[i] for i, key in enumerate(self.x)}
        return new_model

    def addConstr(self, coefs, rhs):
        """
        A method to add new constraint

        Args:
            coefs (ndarray): coeffcients of new constraint
            rhs (float): right-hand side of new constraint

        Returns:
            optModel: new model with the added constraint
        """
        assert len(coefs) == self.num_cost, 'Size of coef vector cannot cost.'
        # copy
        new_model = self.copy()
        # add constraint
        new_model._model.addConstr(gp.quicksum(coefs[i] * new_model.x[k]
                                               for i, k in enumerate(new_model.x))
                                   <= rhs)
        return new_model
