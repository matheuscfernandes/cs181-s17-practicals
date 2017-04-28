# Imports.
import numpy as np
import numpy.random as npr

from SwingyMonkey import SwingyMonkey

class Learner(object):
    '''
    This agent jumps randomly.
    '''

    def __init__(self,Space_Discretization,Eps,Gamma,Eta,ii):
        self.reset(ii) #RESETING CERTAIN VARIABLES THAT ARE NOT INCLUDED IN THIS LIST
        self.Space_Discretization=Space_Discretization
        self.velocity_segments=5
        self.max_V=40
        self.Eps=Eps
        self.Gamma=Gamma
        self.Eta=Eta
        self.screen_width=600
        self.screen_height=400
        self.Q=np.zeros((2,self.velocity_segments+1,
            int(self.screen_width/self.Space_Discretization)+1,
            int(self.screen_height*1.5/self.Space_Discretization)+1,2))

    def reset(self,ii):
        self.epoch=ii
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.gravity = None


    def __random_act(self): #Generating random action for exploration
        return npr.choice([0,1])
    
    def __MeasureGravity(self,state,last_state): #MEASURING GRAVITY
        return (state['monkey']['vel']-last_state['monkey']['vel'])
    
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
        if Dist<0:Dist = 0
        Height=int((state['monkey']['bot']-state['tree']['bot']+0.5*self.screen_height)/Space_Discretization)
        if Height<0:print ("heigt<0")
        Vel=self.__VelocityNorm(state['monkey']['vel'])

        if self.last_action==None: new_action=0
        else:
                last_state=self.last_state

                ### ---- Obtaining Previous State Parameters ---- ####
                LastDist=int(last_state['tree']['dist']/Space_Discretization)
                if Dist<0:Dist = 0
                LastHeight=int((last_state['monkey']['bot']-last_state['tree']['bot']+0.5*self.screen_height)/Space_Discretization)
                # if LastHeight<0:LastHeight = 0
                LastVel=self.__VelocityNorm(last_state['monkey']['vel'])

                #IMPLEMENTATION OF GRAVITY
                if self.gravity==None:
                    Grav=self.__MeasureGravity(state,last_state)
                    if Grav==-1: self.gravity=0
                    elif Grav==-4: self.gravity=1


                #EPSILONG GREEDY IMPLEMENTATION    
                if npr.rand()<self.Eps: new_action=self.__random_act()
                else: new_action=np.argmax(self.Q[:,Vel,Dist,Height,self.gravity])
  
                #Q-UPDATE
                Q_Max=np.max(self.Q[:,Vel,Dist,Height,self.gravity])
                self.Q[self.last_action,LastVel,LastDist,LastHeight,self.gravity]-=self.Eta*(self.Q[self.last_action,LastVel,LastDist,LastHeight,self.gravity]-(self.last_reward+self.Gamma*Q_Max))  

        self.last_action = new_action
        self.last_state = self.state

        return new_action

    def reward_callback(self, reward):
        '''This gets called so you can see what reward you get.'''
        # if reward==-10: print (self.epoch)
        self.last_reward = reward


def run_games(learner, hist, iters = 100, t_len = 100):
    '''
    Driver function to simulate learning by having the agent play a sequence of games.
    '''
    best_score=0.
    for ii in range(iters):
        # Make a new monkey object.
        swing = SwingyMonkey(sound=False,                  # Don't play sounds.
                             text="Epoch %d \\ Heighest Score %d" % (ii,best_score),       # Display the epoch on screen.
                             tick_length = t_len,          # Make game ticks super fast.
                             action_callback=learner.action_callback,
                             reward_callback=learner.reward_callback)

        # Loop until you hit something.
        while swing.game_loop():
            pass
        
        # Save score history.
        hist.append(swing.score)
        if max(hist)>best_score: 
        	best_score=max(hist)
        	print 'In Epoch {} the max score was beat to {}'.format(ii,max(hist))

        # Reset the state of the learner.
        learner.reset(ii)
        
    return


if __name__ == '__main__':

    #Parameters
    Space_Discretization=50 # space direscretization in terms of pixels
    Eps=0.00001
    Gamma=0.8
    Eta=0.2

    #PRINTING PARAMETERS
    print 'Running Without EPS and ETA Correction'	
    print '----Parameters-----'
    print 'Space_Discretization',Space_Discretization
    print 'Eps',Eps
    print 'Gamma',Gamma
    print 'Eta',Eta
    print '----Score Progress----'

    # Select agent.
    agent = Learner(Space_Discretization,Eps,Gamma,Eta,0)

    # Empty list to save history.
    hist = []

    # Run games. 
    run_games(agent, hist, 1000, 1)

    # Save history. 
    np.save('hist',np.array(hist))