# Imports.
import numpy as np
import numpy.random as npr

from SwingyMonkey import SwingyMonkey

class Learner(object):
    '''
    This agent jumps randomly.
    '''

    def __init__(self,Space_Discretization,Eps,Gamma,Eta):
        self.reset()
        self.Space_Discretization=Space_Discretization
        self.velocity_segments=10
        self.max_V=40
        self.Eps=Eps
        self.Gamma=Gamma
        self.Eta=Eta
        self.screen_width=600
        self.screen_height=400
        self.Q=np.zeros((2,self.velocity_segments+1,int(self.screen_width/self.Space_Discretization)+1,int(self.screen_height/self.Space_Discretization)+1))

    def reset(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.gravity = None

    def action_callback(self, state):
        '''
        Implement this function to learn things and take actions.
        Return 0 if you don't want to jump and 1 if you do.
        '''

        self.state=state
        Space_Discretization=self.Space_Discretization


        def random_act(): #Generating random action for exploration
        	return npr.choice([0,1])
        def MeasureGravity(self,state,last_state):
            return abs(state['monkey']['vel']-last_state['monkey']['vel'])
        def VelocityNorm(self,v):
            Segs=self.velocity_segments
            Max_V=self.max_V
            V_norm=int((float(v)/float(Max_V)+1.)*Segs/2.)
            if V_norm>Segs: V_norm=Segs
            if V_norm<0: V_norm=0
            return V_norm

        ### ---- Obtaining Current State Parameters ---- ####
        Dist=int(state['tree']['dist']/Space_Discretization)
        Height=int((state['monkey']['bot']-state['tree']['bot'])/Space_Discretization)
        Vel=VelocityNorm(state['monkey']['vel'])

        if self.last_action==None: new_action=0
        else:

                last_state=self.last_state

                ### ---- Obtaining Previous State Parameters ---- ####
                LastDist=int(last_state['tree']['dist']/Space_Discretization)
                LastHeight=int((last_state['monkey']['bot']-last_state['tree']['bot'])/Space_Discretization)
                LastVel=VelocityNorm(last_state['monkey']['vel'])

                if self.gravity==None:
                    Grav=MeasureGravity(state,last_state)
                    if Grav<0: self.gravity=int(abs(Grav))

                if npr.rand()<self.eta: new_action=random_act()
                
                else:    

                new_action=

                self.Q[self.last_action]


        
        	

        self.last_action = new_action
        self.last_state  = self.state

        print state
        print new_action


        return self.last_action

    def reward_callback(self, reward):
        '''This gets called so you can see what reward you get.'''
        self.last_reward = reward


def run_games(learner, hist, iters = 100, t_len = 100):
    '''
    Driver function to simulate learning by having the agent play a sequence of games.
    '''
    
    for ii in range(iters):
        # Make a new monkey object.
        swing = SwingyMonkey(sound=False,                  # Don't play sounds.
                             text="Epoch %d" % (ii),       # Display the epoch on screen.
                             tick_length = t_len,          # Make game ticks super fast.
                             action_callback=learner.action_callback,
                             reward_callback=learner.reward_callback)

        # Loop until you hit something.
        while swing.game_loop():
            pass
        
        # Save score history.
        hist.append(swing.score)

        # Reset the state of the learner.
        learner.reset()
        
    return


if __name__ == '__main__':

	#Parameters
	Space_Discretization=100 # space direscretization in terms of pixels
	Eps=0.01
	Gamma=0.9
	Eta=

	# Select agent.
	agent = Learner(Space_Discretization,Eps,Gamma,Eta)

	# Empty list to save history.
	hist = []

	# Run games. 
	run_games(agent, hist, 20, 1000)

	# Save history. 
	np.save('hist',np.array(hist))


