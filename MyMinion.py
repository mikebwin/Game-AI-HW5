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
		enemy_towers = self.agent.world.getEnemyTowers(self.agent.getTeam())
		enemy_base = self.agent.world.getEnemyBases(self.agent.getTeam())[0]

		# gotta go take down the enemy towers first
		if len(enemy_towers) == 2:
			which_tower = random.randint(0, 1)
			self.agent.changeState(MoveToTower, enemy_towers[which_tower])

		# if enemy_towers[0].getHitpoints() == 0:
		# 	self.agent.changeState(MoveToTower, enemy_towers[0], enemy_base)
		#
		# if enemy_towers[1].getHitpoints() == 0:
		# 	self.agent.changeState(MoveToTower, enemy_towers[0], enemy_base)

		elif len(enemy_towers) == 1:
			if enemy_towers[0].getHitpoints() != 0:
				# print "moving to enemy tower 1"
				self.agent.changeState(MoveToTower, enemy_towers[0])
			else:
				# print "moving to enemy tower 2"
				self.agent.changeState(MoveToTower, enemy_towers[1])

		elif enemy_base:
			# print "moving to enemy base"
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

class MoveToTower(State):

	def parseArgs(self, args):
		self.targetTower = args[0]

	def enter(self, oldstate):
		State.enter(self, oldstate)
		self.agent.navigateTo(self.targetTower.getLocation())

	def execute(self, delta = 0):
		if self.agent.isMoving() is not True:
			self.agent.navigateTo(self.targetTower.getLocation())

		if not self.targetTower.alive:
			self.agent.changeState(Idle)

		if distance(self.agent.getLocation(), self.targetTower.getLocation()) <= SMALLBULLETRANGE:
			# print "shooting at tower"
			self.agent.stopMoving()
			self.agent.turnToFace(self.targetTower.getLocation())
			self.agent.shoot()

	def exit(self):
		self.agent.stopMoving()


class MoveToBase(State):

	def parseArgs(self, args):
		self.targetBase = args[0]

	def enter(self, oldstate):
		State.enter(self, oldstate)
		self.agent.navigateTo(self.targetBase.getLocation())

	def execute(self, delta = 0):
		if self.agent.isMoving() is not True:
			self.agent.navigateTo(self.targetBase.getLocation())

		if not self.targetBase.alive:
			self.agent.changeState(Idle)

		if distance(self.agent.getLocation(), self.targetBase.getLocation()) <= BIGBULLETRANGE:
			# print "shooting at base"
			self.agent.stopMoving()
			self.agent.turnToFace(self.targetBase.getLocation())
			self.agent.shoot()

	def exit(self):
		self.agent.stopMoving()

