from .core import Observation, analogue_forecast, brier_up, seldon_deviation

def main():
    raw=[(.2,.8,100),(.4,.6,102),(.7,.3,99),(.3,.7,103),(.8,.2,98),(.45,.55,101),(.75,.25,97),(.5,.5,100)]
    h=[Observation(i,i,{"stress":s,"growth":g,"target":y}) for i,(s,g,y) in enumerate(raw)]
    f=analogue_forecast(h,6,"target",("stress","growth"),k=3)
    actual=h[7].values["target"]/h[6].values["target"]-1
    print({"analogues":f.analogue_times,"mean":f.mean,"p_up":f.probability_above(),
           "actual":actual,"brier":brier_up(f,actual),"seldon_deviation":seldon_deviation(f,actual)})

if __name__=="__main__": main()
