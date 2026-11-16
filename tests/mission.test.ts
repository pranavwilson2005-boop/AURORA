import test from 'node:test';
import assert from 'node:assert/strict';
import {fresh} from '../src/game/GameState.ts';
import {tick} from '../src/game/GameEngine.ts';

test('mission clock advances one day every ten minutes',()=>{
  let state=fresh('Test Commander');
  for(let i=0;i<599;i++)state=tick(state,1);
  assert.equal(state.day,1);
  state=tick(state,1);
  assert.equal(state.day,2);
  assert.equal(state.elapsedSeconds,600);
});

test('first timed incident arrives during day one',()=>{
  let state=fresh();
  for(let i=0;i<155;i++)state=tick(state,1);
  assert.ok(state.incident);
  assert.match(state.event,/detected|fault|clogged|reduced/);
});

test('mission ends after seven in-game days',()=>{
  let state=fresh();
  for(let i=0;i<4200&&!state.won&&!state.lost;i++)state=tick(state,1);
  assert.equal(state.elapsedSeconds,4200);
  assert.equal(state.day,7);
  assert.equal(state.won,true);
});

test('resources and crop progress change without a manual day action',()=>{
  let state=fresh();
  const initialWater=state.resources.water;
  const initialFood=state.resources.food;
  for(let i=0;i<600;i++)state=tick(state,1);
  assert.notEqual(state.resources.water,initialWater);
  assert.notEqual(state.resources.food,initialFood);
  assert.ok(state.cropProgress>0);
});
