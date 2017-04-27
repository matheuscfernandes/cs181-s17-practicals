# Imports.
import numpy as np
import numpy.random as npr

from SwingyMonkey import SwingyMonkey

class Learner(object):
    '''
    This agent jumps randomly.
    '''

    def __init__(self,Space_Discretization,Eps,Gamma,Eta):
        self.reset() #RESETING CERTAIN VARIABLES THAT ARE NOT INCLUDED IN THIS LIST
        self.Space_Discretization=Space_Discretization
        self.velocity_segments=10
        self.max_V=40
        self.Eps=Eps
        self.Gamma=Gamma
        self.Eta=Eta
        self.screen_width=600
        self.screen_height=400
        self.Q=np.zeros((2,self.velocity_segments+1,int(self.screen_width/self.Space_Discretization)+1,
                        int(self.screen_height/self.Space_Discretization)+1),2)

    def reset(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.gravity = None


    def __random_act(): #Generating random action for exploration
        return npr.choice([0,1])
    
    def __MeasureGravity(self,state,last_state): #MEASURING GRAVITY
        return abs(state['monkey']['vel']-last_state['monkey']['vel'])
    
    def __VelocityNorm(self,v): #NORMALIZING VELOCITY INTO DIFFERENT INDECES FOR CALLING Q FUNCTION
        Segs=self.velocity_segments
        Max_V=self.max_V
        V_norm=int((float(v)/float(Max_V)+1.)*Segs/2.)
        if V_norm>Segs: V_norm=Segs
        if V_norm<0: V_norm=0
        return V_norm

    def action_callback(self, state):
        '''
        Implement this function to learn things and take actions.
        Return 0 if you don't want to jump and 1 if you do.
        '''
        #INITIALIZING FREQUENTLY USED VARIABLES
        self.state=state
        Space_Discretization=self.Space_Discretization

        ### ---- Obtaining Current State Parameters ---- ####
        Dist=int(state['tree']['dist']/Space_Discretization)
        Height=int((state['monkey']['bot']-state['tree']['bot'])/Space_Discretization)
        Vel=self.__VelocityNorm(state['monkey']['vel'])

        if self.last_action==None: new_action=0
        else:
                last_state=self.last_state

                ### ---- Obtaining Previous State Parameters ---- ####
                LastDist=int(last_state['tree']['dist']/Space_Discretization)
                LastHeight=int((last_state['monkey']['bot']-last_state['tree']['bot'])/Space_Discretization)
                LastVel=self.__VelocityNorm(last_state['monkey']['vel'])

                #IMPLEMENTATION OF GRAVITY
                if self.gravity==None:
                    Grav=self.__MeasureGravity(state,last_state)
                    if Grav==-1: self.gravity=0
                    elif Grav==-4: self.gravity=1


                #EPSILONG GREEDY IMPLEMENTATION    
                if npr.rand()<self.Eps: new_action=random_act()
                else: new_action=np.argmax(self.Q[:,Vel,Dist,Height,self.gravity])

                #Q-UPDATE
                Q_Max=np.max(self.Q[:,Vel,Dist,Height,self.gravity])
                self.Q[self.last_action,Vel,Dist,Height,self.gravity] -= 
                        self.eta*(self.Q[self.last_action,Vel,Dist,Height,self.gravity]-(self.last_reward+self.Gamma*Q_Max))  

        self.last_action = new_action
        self.last_state  = self.state

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


