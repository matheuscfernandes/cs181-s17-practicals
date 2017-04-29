# Imports.
import numpy as np
import numpy.random as npr

from SwingyMonkey import SwingyMonkey

class Learner(object):
    '''
    This agent jumps randomly.
    '''

    def __init__(self,Space_Discretization,Eps_0,Gamma,Eta,ii):
        self.reset(ii) #RESETING CERTAIN VARIABLES THAT ARE NOT INCLUDED IN THIS LIST
        self.Space_Discretization=Space_Discretization
        self.velocity_segments=5
        self.max_V=40
        self.Eps_0=Eps_0
        self.Gamma=Gamma
        self.Eta_0=Eta_0
        self.screen_width=600
        self.screen_height=400
        self.Q=np.zeros((2,self.velocity_segments+1,
            int(self.screen_width/self.Space_Discretization)+1,
            int(self.screen_height*1.5/self.Space_Discretization)+1,2))
        self.C=np.zeros((2,self.velocity_segments+1,
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
                # epsilon-greedy
                new_action=np.argmax(self.Q[:,Vel,Dist,Height,self.gravity])
                if self.C[new_action,Vel,Dist,Height,self.gravity] > 0:
                    # devide eps by number of times this action has been taken 
                    # more times it has been taken, smaller the eps
                    Eps = Eps_0/self.C[new_action,Vel,Dist,Height,self.gravity]
                    
                else:
                    # If never been taken, randomly chose.
                    Eps = Eps_0

                if self.C[self.last_action,LastVel,LastDist,LastHeight,self.gravity]>0:
                    Eta = Eta_0/self.C[self.last_action,LastVel,LastDist,LastHeight,self.gravity]
                else:
                    Eta = Eta_0
                # eps probability 

                #EPSILONG GREEDY IMPLEMENTATION    
                if npr.rand()<Eps: new_action=self.__random_act()
  
                #Q-UPDATE
                Q_Max=np.max(self.Q[:,Vel,Dist,Height,self.gravity])
                self.Q[self.last_action,LastVel,LastDist,LastHeight,self.gravity]-=Eta*(self.Q[self.last_action,LastVel,LastDist,LastHeight,self.gravity]-(self.last_reward+self.Gamma*Q_Max))  

        self.last_action = new_action
        self.last_state = self.state
        self.C[new_action,Vel,Dist,Height,self.gravity] += 1
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
                             text="Epoch %d" % (ii),       # Display the epoch on screen.
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
            print ('In Epoch {} the max score was beat to {}'.format(ii,max(hist)))

        # Reset the state of the learner.
        learner.reset(ii)
        
    return


if __name__ == '__main__':

	#Parameters
    Space_Discretization=50 # space direscretization in terms of pixels
    Eps_0=0.01
    Gamma=0.9
    Eta_0=0.2
    listeps = [0.001,0.005,0.01,0.05,0.1]
    listga = [0.8,0.95]
    listeta = [0.1,0.5]
    # print ('Running With EPS and ETA Correction')
    # print ('----Parameters-----')
    # print ('Space_Discretization',Space_Discretization)
    # print ('Eps',Eps_0)
    # print ('Gamma',Gamma)
    # print ('Eta',Eta_0)
    # print ('----Score Progress----')
	# Select agent.
    for Eps_0 in listeps:
        agent = Learner(Space_Discretization,Eps_0,Gamma,Eta_0,0)

            	# Empty list to save history.
        hist = []

            	# Run games. 
        run_games(agent, hist, 300, 1)

            	# Save history.
        filename = 'hist2_eps'+str(10000*Eps_0)+'_ga'+ str(10000*Gamma)+'_eta'+str(10000*Eta_0)
        np.save(filename,np.array(hist))
    Eps_0=0.01
    Gamma=0.9
    Eta_0=0.2
    for Gamma in listga:
        agent = Learner(Space_Discretization,Eps_0,Gamma,Eta_0,0)

                # Empty list to save history.
        hist = []

                # Run games. 
        run_games(agent, hist, 300, 1)

                # Save history.
        filename = 'hist2_eps'+str(10000*Eps_0)+'_ga'+ str(10000*Gamma)+'_eta'+str(10000*Eta_0)
        np.save(filename,np.array(hist))
    Eps_0=0.01
    Gamma=0.9
    Eta_0=0.2
    for Eta_0 in listeta:
        agent = Learner(Space_Discretization,Eps_0,Gamma,Eta_0,0)

                # Empty list to save history.
        hist = []

                # Run games. 
        run_games(agent, hist, 300, 1)

                # Save history.
        filename = 'hist2_eps'+str(10000*Eps_0)+'_ga'+ str(10000*Gamma)+'_eta'+str(10000*Eta_0)
        np.save(filename,np.array(hist))

python plotter.py 50 hist1_eps0.001_ga0.9_eta0.2 hist1_eps0.005_ga0.9_eta0.2 hist1_eps0.01_ga0.9_eta0.2 hist1_eps0.05_ga0.9_eta0.2 hist1_eps0.1_ga0.9_eta0.2
python plotter.py 50 hist1_eps0.01_ga0.8_eta0.2 hist1_eps0.01_ga0.9_eta0.2 hist1_eps0.01_ga0.95_eta0.2
python plotter.py 50 hist1_eps0.01_ga0.9_eta0.1 hist1_eps0.01_ga0.9_eta0.1
