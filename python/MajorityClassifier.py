import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score

_CLASSIFIERS = {'svm': SVC,
                'knn': KNeighborsClassifier,
                'mnb': MultinomialNB,
                'rf': RandomForestClassifier,
                'mlp': MLPClassifier}

"""A refactored majority classifier that inherits from base classifiers and 
allows for better integration with other scikit tools"""
class MajorityClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, algs=None, params={}, weighted=False, folds=3):
        if not algs:
            algs = ['svm','knn','mnb','rf','mlp']
        if not params:
            params = {'svm': {}, 'knn': {}, 'mnb': {}, 'rf': {},'mlp': {}}
        self.classifiers = [_CLASSIFIERS[a](**(params[a])) for a in algs]
        self.weighted = weighted
        self.weights = [1]*len(algs)
        self.folds = folds

    def fit(self, X, y=None):
        for i, clf in enumerate(self.classifiers):
            clf.fit(X, np.ravel(y))
            if self.weighted:
                self.weights[i] = cross_val_score(clf, X, np.ravel(y), cv=self.folds).mean()

    def predict(self, X):
        return np.apply_along_axis(axis=1,
                                   arr=np.array(X),
                                   func1d=lambda x:
                                   self._count(np.concatenate([c.predict([x]) for c in self.classifiers])).argmax(),
                                   )

    def score(self, X, y=None, sample_weight=None):
        y_pred = self.predict(X)
        y_val = y.as_matrix().flatten()
        tp = 0
        for i in range(0,len(y)):
            tp += y_pred[i] == y_val[i]
        res = tp/len(y_val)
        return res

    def _count(self, votes):
        res = np.bincount(votes)
        if self.weighted:
            res = np.zeros((1, len(res)))
            for i, vote in enumerate(votes):
                res[0,vote] += self.weights[i]
        return res

"""
    params_grid = [{'a1': [None, 'svm'], 'p11' : ['linear', 'poly', 'rbf', 'sigmoid'], 'p12': [1,10,100,1000],
                    'a2': [None, 'rf'], 'p41': [10, 30, 50, 100], 'p42': [None, 1, 3],
                    'a3': [None, 'knn'], 'p21': [1,3,5,8,10,30], 'p22': ['uniform', 'distance'],
                    'a4': [None, 'mnb'],
                    'a5': [None, 'mlp'], 'p51': ['identity', 'relu', 'logistic'], 'p52': [0.001, 1.0000000000000001e-05, 9.9999999999999995e-07]}]
    def __init__(self,
                 a1=None, p11 = None, p12=None,
                 a2=None, p21 = None, p22=None,
                 a3=None, p31 = None, p32=None,
                 a4=None,
                 a5=None, p51 = None, p52=None,
                 weighted=False, folds=3):
        algs = []
        params = {}
        if a1:
            algs.append(a1)
            params[a1] = {'kernel': p11, 'C': p12}
        if a2:
            algs.append(a2)
            params[a2] = {'n_estimators': p21, 'max_depth': p22}
        if a3:
            algs.append(a3)
            params[a3] = {'n_neighbors': p31, 'weights': p32}
        if a4:
            algs.append(a4)
            params[a4] = {}
        if a5:
            algs.append(a5)
            params[a5] = {'activation': p51, 'alpha': p52}
        self.classifiers = [_CLASSIFIERS[a](**(params[a])) for a in algs]
        self.weighted = weighted
        self.weights = [1] * len(algs)
        self.folds = folds
    """