'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from moba import *

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.states.append(MoveToTower)
		self.states.append(MoveToBase)
		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)





############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###

		# get the enemy towers and bases
		enemy_towers = self.agent.world.getEnemyTowers(self.agent.getTeam())
		enemy_bases = self.agent.world.getEnemyBases(self.agent.getTeam())

		# gotta go take down the enemy towers first

		# if there are 2 enemy towers, randomly choose one of them to go to
		if len(enemy_towers) == 2:
			which_tower = random.randint(0, 1)
			self.agent.changeState(MoveToTower, enemy_towers[which_tower])

		# if 1 tower left, go to that one
		elif len(enemy_towers) == 1:
			if enemy_towers[0].getHitpoints() != 0:
				# print "moving to enemy tower 1"
				self.agent.changeState(MoveToTower, enemy_towers[0])
			else:
				# print "moving to enemy tower 2"
				self.agent.changeState(MoveToTower, enemy_towers[1])

		# when towers are gone, go attack the base
		elif enemy_bases:
			# print "moving to enemy base"
			enemy_base = enemy_bases[0]
			self.agent.changeState(MoveToBase, enemy_base)


		### YOUR CODE GOES ABOVE HERE ###
		return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print "Hey " + str(self.victim) + ", I don't like you!"
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

# go attack one of the enemy towers
class MoveToTower(State):

	def parseArgs(self, args):
		self.targetTower = args[0]

	# coming into this state = go to Tower
	def enter(self, oldstate):
		State.enter(self, oldstate)
		self.agent.navigateTo(self.targetTower.getLocation())

	def execute(self, delta = 0):
		# if the agent is not moving, make it move towards tower
		if self.agent.isMoving() is not True:
			self.agent.navigateTo(self.targetTower.getLocation())

		# if the tower it's going to is dead, go back to Idle to see what to do next
		if not self.targetTower.alive:
			self.agent.changeState(Idle)

		# get ready for firing, not a moment to waste
		self.agent.turnToFace(self.targetTower.getLocation())

		# if within firing range, stop, turn, and shoot
		if distance(self.agent.getLocation(), self.targetTower.getLocation()) <= SMALLBULLETRANGE:
			# print "shooting at tower"
			self.agent.stopMoving()
			self.agent.turnToFace(self.targetTower.getLocation())
			self.agent.shoot()

		# if not within range of tower, constantly look for enemy minions and shoot at them
		else:
			for npc in self.agent.getVisibleType(Minion):
				if npc in self.agent.world.getEnemyNPCs(self.agent.getTeam()) \
						and distance(self.agent.getLocation(), npc.getLocation()) < SMALLBULLETRANGE:
					self.agent.turnToFace(npc.getLocation())
					self.agent.shoot()

	def exit(self):
		self.agent.stopMoving()


# this state attacks the enemy base
class MoveToBase(State):

	def parseArgs(self, args):
		self.targetBase = args[0]

	# upon entering this state, go to the enemy base
	def enter(self, oldstate):
		State.enter(self, oldstate)
		self.agent.navigateTo(self.targetBase.getLocation())

	def execute(self, delta = 0):

		# if agent not moving, tell it to go to enemy base
		if self.agent.isMoving() is not True:
			self.agent.navigateTo(self.targetBase.getLocation())

		# if the base is dead, victory condition. go to idle - everyone just kinda sits around
		if not self.targetBase.alive:
			self.agent.changeState(Idle)

		# get ready for firing, not a moment to waste
		self.agent.turnToFace(self.targetBase.getLocation())

		# when within firing range of base, turn and shoot
		if distance(self.agent.getLocation(), self.targetBase.getLocation()) <= SMALLBULLETRANGE:
			# print "shooting at base"
			self.agent.stopMoving()
			self.agent.turnToFace(self.targetBase.getLocation())
			self.agent.shoot()

		# if not in firing range of base, find and shoot at enemy minions
		else:
			for npc in self.agent.getVisibleType(Minion):
				if npc in self.agent.world.getEnemyNPCs(self.agent.getTeam()) \
						and distance(self.agent.getLocation(), npc.getLocation()) < SMALLBULLETRANGE:
					self.agent.turnToFace(npc.getLocation())
					self.agent.shoot()

	def exit(self):
		self.agent.stopMoving()

