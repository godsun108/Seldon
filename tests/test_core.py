import unittest
from seldon.core import Observation, analogue_forecast, brier_up
from seldon.quantum_lab import boltzmann_sampler

class TestSeldon(unittest.TestCase):
    def test_information_firewall(self):
        h=[Observation(0,0,{"x":0.0,"y":100}),Observation(1,1,{"x":0.1,"y":101}),
           Observation(2,99,{"x":0.2,"y":102}),Observation(3,3,{"x":0.15,"y":103})]
        f=analogue_forecast(h,3,"y",("x",),k=3)
        self.assertEqual(f.analogue_times,(0,))
    def test_brier_bounded(self):
        h=[Observation(i,i,{"x":float(i%2),"y":100+i}) for i in range(6)]
        f=analogue_forecast(h,4,"y",("x",),k=2)
        self.assertTrue(0<=brier_up(f,.01)<=1)
    def test_sampler_reproducible(self):
        self.assertEqual(boltzmann_sampler([.1,1],20,seed=7),boltzmann_sampler([.1,1],20,seed=7))

if __name__=="__main__": unittest.main()
