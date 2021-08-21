#print('Hello World')

from z3 import*

num_states = 5
num_msrs = 14
num_ieds = 8
num_rtus = 4
num_routers = 1

#critical_nodes = [Bool('node_%s' % i) for i in range(self.top.no_of_nodes)]
#cost = Int('cost')
#model_cost = Int('model_cost')



x = Int('x')
p3 = Bool('p3')
s = Solver()
s.set(unsat_core=True)

s.add(x > 0)
s.add(x != 1)
s.assert_and_track(x < 0, p3)

#s.assert_and_track(x > 0,  'p1')
#s.assert_and_track(x != 1, 'p2')
#s.assert_and_track(x < 0,  p3)

print(s.check())
c = s.unsat_core()
print c