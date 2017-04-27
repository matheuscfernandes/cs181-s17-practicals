# Imports.
import numpy as np
import numpy.random as npr

from SwingyMonkey import SwingyMonkey

class Learner(object):
    '''
    This agent jumps randomly.
    '''

    def __init__(self,Space_Discretization,Eps,Gamma,Eta):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.Space_Discretization=Space_Discretization
        self.Eps=Eps
        self.Gamma=Gamma
        self.Eta=Eta

    def reset(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None

    def action_callback(self, state):
        '''
        Implement this function to learn things and take actions.
        Return 0 if you don't want to jump and 1 if you do.
        '''
        def random_act(): #Generating random action for exploration
        	return npr.choice([0,1])

        #TREE PARAMETERS
        TreeDist=state['tree']['dist']/self.Space_Discretization
        TreeTopDist=state['tree']['top']
        TreeBotDist=state['tree']['bot']
        TreeDist=state['tree']['dist']

        #MONKEY PARAMETERS
        MonkV=state['monkey']['vel']
        MonkHeight=['monkey']['bot']




        if npr.rand()<self.eta: 
        	new_action=random_act()
        	
        else:
            #initialize the parameters



        if self.last_action==None:



       	else:


        new_state  = state


        self.last_action = new_action
        self.last_state  = new_state

        print state
        print new_action


        return self.last_action

    def reward_callback(self, reward):
        '''This gets called so you can see what reward you get.'''
        print reward
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


