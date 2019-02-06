import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table_experiments import DataTable
import plotly.graph_objs as go
 
import pandas as pd
from itertools import compress

import pulp as plp
from io import StringIO


##########################################
# prepare data
##########################################

# read data from this string for easy deployment
rawdata = StringIO("""Number,Pokemon,Type 1,Type 2,HP,ATTACK,DEFENSE,SPEED,SPECIAL,GIF,PNG,Description
1,Bulbasaur,Grass,Poison,45,49,49,45,65,https://play.pokemonshowdown.com/sprites/bwani/bulbasaur.gif,https://play.pokemonshowdown.com/sprites/bw/bulbasaur.png,A strange seed was planted on its back at birth. The plant sprouts and grows with this Pokemon.
2,Ivysaur,Grass,Poison,60,62,63,60,80,https://play.pokemonshowdown.com/sprites/bwani/ivysaur.gif,https://play.pokemonshowdown.com/sprites/bw/ivysaur.png,"Often seen swimming elegantly by lake shores. It is often mistaken for the Japanese monster, Kappa."
3,Venusaur,Grass,Poison,80,82,83,80,100,https://play.pokemonshowdown.com/sprites/bwani/venusaur.gif,https://play.pokemonshowdown.com/sprites/bw/venusaur.png,"Because it stores several kinds of toxic gases in its body, it is prone to exploding without warning."
4,Charmander,Fire,,39,52,43,65,50,https://play.pokemonshowdown.com/sprites/bwani/charmander.gif,https://play.pokemonshowdown.com/sprites/bw/charmander.png,"Obviously prefers hot places. When it rains, steam is said to spout from the tip of its tail."
5,Charmeleon,Fire,,58,64,58,80,65,https://play.pokemonshowdown.com/sprites/bwani/charmeleon.gif,https://play.pokemonshowdown.com/sprites/bw/charmeleon.png,"When it swings its burning tail, it elevates the temperature to unbearably high levels."
6,Charizard,Fire,Flying,78,84,78,100,85,https://play.pokemonshowdown.com/sprites/bwani/charizard.gif,https://play.pokemonshowdown.com/sprites/bw/charizard.png,Spits fire that is hot enough to melt boulders. Known to cause forest fires unintentionally.
7,Squirtle,Water,,44,48,65,43,50,https://play.pokemonshowdown.com/sprites/bwani/squirtle.gif,https://play.pokemonshowdown.com/sprites/bw/squirtle.png,"After birth, its back swells and hardens into a shell. Powerfully sprays foam from its mouth."
8,Wartortle,Water,,59,63,80,58,65,https://play.pokemonshowdown.com/sprites/bwani/wartortle.gif,https://play.pokemonshowdown.com/sprites/bw/wartortle.png,"Often hides in water to stalk unwary prey. For swimming fast, it moves its ears to maintain balance."
9,Blastoise,Water,,79,83,100,78,85,https://play.pokemonshowdown.com/sprites/bwani/blastoise.gif,https://play.pokemonshowdown.com/sprites/bw/blastoise.png,A brutal Pokemon with pressurized water jets on its shell. They are used for high speed tackles.
10,Caterpie,Bug,,45,30,35,45,20,https://play.pokemonshowdown.com/sprites/bwani/caterpie.gif,https://play.pokemonshowdown.com/sprites/bw/caterpie.png,Its short feet are tipped with suction pads that enable it to tirelessly climb slopes and walls.
11,Metapod,Bug,,50,20,55,30,25,https://play.pokemonshowdown.com/sprites/bwani/metapod.gif,https://play.pokemonshowdown.com/sprites/bw/metapod.png,"This Pokemon is vulnerable to attack while its shell is soft, exposing its weak and tender body."
12,Butterfree,Bug,Flying,60,45,50,70,80,https://play.pokemonshowdown.com/sprites/bwani/butterfree.gif,https://play.pokemonshowdown.com/sprites/bw/butterfree.png,"In battle, it flaps its wings at high speed to release highly toxic dust into the air."
13,Weedle,Bug,Poison,40,35,30,50,20,https://play.pokemonshowdown.com/sprites/bwani/weedle.gif,https://play.pokemonshowdown.com/sprites/bw/weedle.png,"Often found in forests, eating leaves. It has a sharp venomous stinger on its head."
14,Kakuna,Bug,Poison,45,25,50,35,25,https://play.pokemonshowdown.com/sprites/bwani/kakuna.gif,https://play.pokemonshowdown.com/sprites/bw/kakuna.png,"Almost incapable of moving, this Pokemon can only harden its shell to protect itself from predators."
15,Beedrill,Bug,Poison,65,80,40,75,45,https://play.pokemonshowdown.com/sprites/bwani/beedrill.gif,https://play.pokemonshowdown.com/sprites/bw/beedrill.png,Flies at high speed and attacks using its large venomous stingers on its forelegs and tail.
16,Pidgey,Normal,Flying,40,45,40,56,35,https://play.pokemonshowdown.com/sprites/bwani/pidgey.gif,https://play.pokemonshowdown.com/sprites/bw/pidgey.png,A common sight in forests and woods. It flaps its wings at ground level to kick up blinding sand.
17,Pidgeotto,Normal,Flying,63,60,55,71,50,https://play.pokemonshowdown.com/sprites/bwani/pidgeotto.gif,https://play.pokemonshowdown.com/sprites/bw/pidgeotto.png,"Very protective of its sprawling territorial area, this Pokemon will fiercely peck at any intruder."
18,Pidgeot,Normal,Flying,83,80,75,91,70,https://play.pokemonshowdown.com/sprites/bwani/pidgeot.gif,https://play.pokemonshowdown.com/sprites/bw/pidgeot.png,"When hunting, it skims the surface of water at high speed to pick off unwary prey such as MAGIKARP."
19,Rattata,Normal,,30,56,35,72,25,https://play.pokemonshowdown.com/sprites/bwani/rattata.gif,https://play.pokemonshowdown.com/sprites/bw/rattata.png,"Bites anything when it attacks. Small and very quick, it is a common sight in many places."
20,Raticate,Normal,,55,81,60,97,50,https://play.pokemonshowdown.com/sprites/bwani/raticate.gif,https://play.pokemonshowdown.com/sprites/bw/raticate.png,It uses its whiskers to maintain its balance. It apparently slows down if they are cut off.
21,Spearow,Normal,Flying,40,60,30,70,31,https://play.pokemonshowdown.com/sprites/bwani/spearow.gif,https://play.pokemonshowdown.com/sprites/bw/spearow.png,Eats bugs in grassy areas. It has to flap its short wings at high speed to stay airborne.
22,Fearow,Normal,Flying,65,90,65,100,61,https://play.pokemonshowdown.com/sprites/bwani/fearow.gif,https://play.pokemonshowdown.com/sprites/bw/fearow.png,"With its huge and magnificent wings, it can keep aloft without ever having to land for rest."
23,Ekans,Poison,,35,60,44,55,40,https://play.pokemonshowdown.com/sprites/bwani/ekans.gif,https://play.pokemonshowdown.com/sprites/bw/ekans.png,"Moves silently and stealthily. Eats the eggs of birds, such as PIDGEY and SPEAROW, whole."
24,Arbok,Poison,,60,85,69,80,65,https://play.pokemonshowdown.com/sprites/bwani/arbok.gif,https://play.pokemonshowdown.com/sprites/bw/arbok.png,It is rumored that the ferocious warning markings on its belly differ from area to area.
25,Pikachu,Electric,,35,55,30,90,50,https://play.pokemonshowdown.com/sprites/bwani/pikachu.gif,https://play.pokemonshowdown.com/sprites/bw/pikachu.png,"When several of these Pokemon gather, their electricity could build and cause lightning storms."
26,Raichu,Electric,,60,90,55,100,90,https://play.pokemonshowdown.com/sprites/bwani/raichu.gif,https://play.pokemonshowdown.com/sprites/bw/raichu.png,Its long tail serves as a ground to protect itself from its own high voltage power.
27,Sandshrew,Ground,,50,75,85,40,30,https://play.pokemonshowdown.com/sprites/bwani/sandshrew.gif,https://play.pokemonshowdown.com/sprites/bw/sandshrew.png,Burrows deep underground in arid locations far from water. It only emerges to hunt for food.
28,Sandslash,Ground,,75,100,110,65,55,https://play.pokemonshowdown.com/sprites/bwani/sandslash.gif,https://play.pokemonshowdown.com/sprites/bw/sandslash.png,Curls up into a spiny ball when threatened. It can roll while curled up to attack or escape.
29,NidoranF,Poison,,55,47,52,41,40,https://play.pokemonshowdown.com/sprites/bwani/nidoranf.gif,https://play.pokemonshowdown.com/sprites/bw/nidoranf.png,"Although small, its venomous barbs render this Pokemon dangerous. The female has smaller horns."
30,Nidorina,Poison,,70,62,67,56,55,https://play.pokemonshowdown.com/sprites/bwani/nidorina.gif,https://play.pokemonshowdown.com/sprites/bw/nidorina.png,The female's horn develops slowly. Prefers physical attacks such as clawing and biting.
31,Nidoqueen,Poison,Ground,90,82,87,76,75,https://play.pokemonshowdown.com/sprites/bwani/nidoqueen.gif,https://play.pokemonshowdown.com/sprites/bw/nidoqueen.png,Its hard scales provide strong protection. It uses its hefty bulk to execute powerful moves.
32,NidoranM,Poison,,46,57,40,50,40,https://play.pokemonshowdown.com/sprites/bwani/nidoranm.gif,https://play.pokemonshowdown.com/sprites/bw/nidoranm.png,"Stiffens its ears to sense danger. The larger its horns, the more powerful its secreted venom."
33,Nidorino,Poison,,61,72,57,65,55,https://play.pokemonshowdown.com/sprites/bwani/nidorino.gif,https://play.pokemonshowdown.com/sprites/bw/nidorino.png,An aggressive Pokemon that is quick to attack. The horn on its head secretes a powerful venom.
34,Nidoking,Poison,Ground,81,92,77,85,75,https://play.pokemonshowdown.com/sprites/bwani/nidoking.gif,https://play.pokemonshowdown.com/sprites/bw/nidoking.png,"It uses its powerful tail in battle to smash, constrict, then break the prey's bones."
35,Clefairy,Normal,,70,45,48,35,60,https://play.pokemonshowdown.com/sprites/bwani/clefairy.gif,https://play.pokemonshowdown.com/sprites/bw/clefairy.png,Its magical and cute appeal has many admirers. It is rare and found only in certain areas.
36,Clefable,Normal,,95,70,73,60,85,https://play.pokemonshowdown.com/sprites/bwani/clefable.gif,https://play.pokemonshowdown.com/sprites/bw/clefable.png,A timid fairy Pokemon that is rarely seen. It will run and hide the moment it senses people.
37,Vulpix,Fire,,38,41,40,65,65,https://play.pokemonshowdown.com/sprites/bwani/vulpix.gif,https://play.pokemonshowdown.com/sprites/bw/vulpix.png,"At the time of birth, it has just one tail. The tail splits from its tip as it grows older."
38,Ninetales,Fire,,73,76,75,100,100,https://play.pokemonshowdown.com/sprites/bwani/ninetales.gif,https://play.pokemonshowdown.com/sprites/bw/ninetales.png,Very smart and very vengeful. Grabbing one of its many tails could result in a 1000-year curse.
39,Jigglypuff,Normal,,115,45,20,20,25,https://play.pokemonshowdown.com/sprites/bwani/jigglypuff.gif,https://play.pokemonshowdown.com/sprites/bw/jigglypuff.png,"When its huge eyes light up, it sings a mysteriously soothing melody that lulls its enemies to sleep."
40,Wigglytuff,Normal,,140,70,45,45,50,https://play.pokemonshowdown.com/sprites/bwani/wigglytuff.gif,https://play.pokemonshowdown.com/sprites/bw/wigglytuff.png,"The body is soft and rubbery. When angered, it will suck in air and inflate itself to an enormous size."
41,Zubat,Poison,Flying,40,45,35,55,40,https://play.pokemonshowdown.com/sprites/bwani/zubat.gif,https://play.pokemonshowdown.com/sprites/bw/zubat.png,Forms colonies in perpetually dark places. Uses ultrasonic waves to identify and approach targets.
42,Golbat,Poison,Flying,75,80,70,90,75,https://play.pokemonshowdown.com/sprites/bwani/golbat.gif,https://play.pokemonshowdown.com/sprites/bw/golbat.png,"Once it strikes, it will not stop draining energy from the victim even if it gets too heavy to fly."
43,Oddish,Grass,Poison,45,50,55,30,75,https://play.pokemonshowdown.com/sprites/bwani/oddish.gif,https://play.pokemonshowdown.com/sprites/bw/oddish.png,"During the day, it keeps its face buried in the ground. At night, it wanders around sowing its seeds."
44,Gloom,Grass,Poison,60,65,70,40,85,https://play.pokemonshowdown.com/sprites/bwani/gloom.gif,https://play.pokemonshowdown.com/sprites/bw/gloom.png,The fluid that oozes from its mouth isn't drool. It is a nectar that is used to attract prey.
45,Vileplume,Grass,Poison,75,80,85,50,100,https://play.pokemonshowdown.com/sprites/bwani/vileplume.gif,https://play.pokemonshowdown.com/sprites/bw/vileplume.png,"The larger its petals, the more toxic pollen it contains. Its big head is heavy and hard to hold up."
46,Paras,Bug,Grass,35,70,55,25,55,https://play.pokemonshowdown.com/sprites/bwani/paras.gif,https://play.pokemonshowdown.com/sprites/bw/paras.png,Burrows to suck tree roots. The mushrooms on its back grow by drawing nutrients from the bug host.
47,Parasect,Bug,Grass,60,95,80,30,80,https://play.pokemonshowdown.com/sprites/bwani/parasect.gif,https://play.pokemonshowdown.com/sprites/bw/parasect.png,A host-parasite pair in which the parasite mushroom has taken over the host bug. Prefers damp places.
48,Venonat,Bug,Poison,60,55,50,45,40,https://play.pokemonshowdown.com/sprites/bwani/venonat.gif,https://play.pokemonshowdown.com/sprites/bw/venonat.png,Lives in the shadows of tall trees where it eats insects. It is attracted by light at night.
49,Venomoth,Bug,Poison,70,65,60,90,90,https://play.pokemonshowdown.com/sprites/bwani/venomoth.gif,https://play.pokemonshowdown.com/sprites/bw/venomoth.png,The dust-like scales covering its wings are color coded to indicate the kinds of poison it has.
50,Diglett,Ground,,10,55,25,95,45,https://play.pokemonshowdown.com/sprites/bwani/diglett.gif,https://play.pokemonshowdown.com/sprites/bw/diglett.png,Lives about one yard underground where it feeds on plant roots. It sometimes appears above ground.
51,Dugtrio,Ground,,35,80,50,120,70,https://play.pokemonshowdown.com/sprites/bwani/dugtrio.gif,https://play.pokemonshowdown.com/sprites/bw/dugtrio.png,A team of DIGLETT triplets. It triggers huge earthquakes by burrowing 60 miles underground.
52,Meowth,Normal,,40,45,35,90,40,https://play.pokemonshowdown.com/sprites/bwani/meowth.gif,https://play.pokemonshowdown.com/sprites/bw/meowth.png,Adores circular objects. Wanders the streets on a nightly basis to look for dropped loose change.
53,Persian,Normal,,65,70,60,115,65,https://play.pokemonshowdown.com/sprites/bwani/persian.gif,https://play.pokemonshowdown.com/sprites/bw/persian.png,"Although its fur has many admirers, it is tough to raise as a pet because of its fickle meanness."
54,Psyduck,Water,,50,52,48,55,50,https://play.pokemonshowdown.com/sprites/bwani/psyduck.gif,https://play.pokemonshowdown.com/sprites/bw/psyduck.png,"While lulling its enemies with its vacant look, this wily Pokemon will use psychokinetic powers."
55,Golduck,Water,,80,82,78,85,80,https://play.pokemonshowdown.com/sprites/bwani/golduck.gif,https://play.pokemonshowdown.com/sprites/bw/golduck.png,"Often seen swimming elegantly by lake shores. It is often mistaken for the Japanese monster, Kappa."
56,Mankey,Fighting,,40,80,35,70,35,https://play.pokemonshowdown.com/sprites/bwani/mankey.gif,https://play.pokemonshowdown.com/sprites/bw/mankey.png,Extremely quick to anger. It could be docile one moment then thrashing away the next instant.
57,Primeape,Fighting,,65,105,60,95,60,https://play.pokemonshowdown.com/sprites/bwani/primeape.gif,https://play.pokemonshowdown.com/sprites/bw/primeape.png,Always furious and tenacious to boot. It will not abandon chasing its quarry until it is caught.
58,Growlithe,Fire,,55,70,45,60,50,https://play.pokemonshowdown.com/sprites/bwani/growlithe.gif,https://play.pokemonshowdown.com/sprites/bw/growlithe.png,Very protective of its territory. It will bark and bite to repel intruders from its space.
59,Arcanine,Fire,,90,110,80,95,80,https://play.pokemonshowdown.com/sprites/bwani/arcanine.gif,https://play.pokemonshowdown.com/sprites/bw/arcanine.png,A Pokemon that has been admired since the past for its beauty. It runs agilely as if on wings.
60,Poliwag,Water,,40,50,40,90,40,https://play.pokemonshowdown.com/sprites/bwani/poliwag.gif,https://play.pokemonshowdown.com/sprites/bw/poliwag.png,Its newly grown legs prevent it from running. It appears to prefer swimming than trying to stand.
61,Poliwhirl,Water,,65,65,65,90,50,https://play.pokemonshowdown.com/sprites/bwani/poliwhirl.gif,https://play.pokemonshowdown.com/sprites/bw/poliwhirl.png,"Capable of living in or out of water. When out of water, it sweats to keep its body slimy."
62,Poliwrath,Water,Fighting,90,85,95,70,70,https://play.pokemonshowdown.com/sprites/bwani/poliwrath.gif,https://play.pokemonshowdown.com/sprites/bw/poliwrath.png,An adept swimmer at both the front crawl and breast stroke. Easily overtakes the best human swimmers.
63,Abra,Psychic,,25,20,15,90,105,https://play.pokemonshowdown.com/sprites/bwani/abra.gif,https://play.pokemonshowdown.com/sprites/bw/abra.png,"Using its ability to read minds, it will identify impending danger and TELEPORT to safety."
64,Kadabra,Psychic,,40,35,30,105,120,https://play.pokemonshowdown.com/sprites/bwani/kadabra.gif,https://play.pokemonshowdown.com/sprites/bw/kadabra.png,It emits special alpha waves from its body that induce headaches just by being close by.
65,Alakazam,Psychic,,55,50,45,120,135,https://play.pokemonshowdown.com/sprites/bwani/alakazam.gif,https://play.pokemonshowdown.com/sprites/bw/alakazam.png,"Its brain can outperform a supercomputer. Its intelligence quotient is said to be 5,000."
66,Machop,Fighting,,70,80,50,35,35,https://play.pokemonshowdown.com/sprites/bwani/machop.gif,https://play.pokemonshowdown.com/sprites/bw/machop.png,Loves to build its muscles. It trains in all styles of martial arts to become even stronger.
67,Machoke,Fighting,,80,100,70,45,50,https://play.pokemonshowdown.com/sprites/bwani/machoke.gif,https://play.pokemonshowdown.com/sprites/bw/machoke.png,"Its muscular body is so powerful, it must wear a power save belt to be able to regulate its motions."
68,Machamp,Fighting,,90,130,80,55,65,https://play.pokemonshowdown.com/sprites/bwani/machamp.gif,https://play.pokemonshowdown.com/sprites/bw/machamp.png,"Using its heavy muscles, it throws powerful punches that can send the victim clear over the horizon."
69,Bellsprout,Grass,Poison,50,75,35,40,70,https://play.pokemonshowdown.com/sprites/bwani/bellsprout.gif,https://play.pokemonshowdown.com/sprites/bw/bellsprout.png,A carnivorous Pokemon that traps and eats bugs. It uses its root feet to soak up needed moisture.
70,Weepinbell,Grass,Poison,65,90,50,55,85,https://play.pokemonshowdown.com/sprites/bwani/weepinbell.gif,https://play.pokemonshowdown.com/sprites/bw/weepinbell.png,It spits out POISONPOWDER to immobilize the enemy and then finishes it with a spray of ACID.
71,Victreebel,Grass,Poison,80,105,65,70,100,https://play.pokemonshowdown.com/sprites/bwani/victreebel.gif,https://play.pokemonshowdown.com/sprites/bw/victreebel.png,"Said to live in huge colonies deep in jungles, although no one has ever returned from there."
72,Tentacool,Water,Poison,40,40,35,70,100,https://play.pokemonshowdown.com/sprites/bwani/tentacool.gif,https://play.pokemonshowdown.com/sprites/bw/tentacool.png,Drifts in shallow seas. Anglers who hook them by accident are often punished by its stinging acid.
73,Tentacruel,Water,Poison,80,70,65,100,120,https://play.pokemonshowdown.com/sprites/bwani/tentacruel.gif,https://play.pokemonshowdown.com/sprites/bw/tentacruel.png,"The tentacles are normally kept short. On hunts, they are extended to ensnare and immobilize prey."
74,Geodude,Rock,Ground,40,80,100,20,30,https://play.pokemonshowdown.com/sprites/bwani/geodude.gif,https://play.pokemonshowdown.com/sprites/bw/geodude.png,"Found in fields and mountains. Mistaking them for boulders, people often step or trip on them."
75,Graveler,Rock,Ground,55,95,115,35,45,https://play.pokemonshowdown.com/sprites/bwani/graveler.gif,https://play.pokemonshowdown.com/sprites/bw/graveler.png,Rolls down slopes to move. It rolls over any obstacle without slowing or changing its direction.
76,Golem,Rock,Ground,80,110,130,45,55,https://play.pokemonshowdown.com/sprites/bwani/golem.gif,https://play.pokemonshowdown.com/sprites/bw/golem.png,Its boulder-like body is extremely hard. It can easily withstand dynamite blasts without damage.
77,Ponyta,Fire,,50,85,55,90,65,https://play.pokemonshowdown.com/sprites/bwani/ponyta.gif,https://play.pokemonshowdown.com/sprites/bw/ponyta.png,Its hooves are 10 times harder than diamonds. It can trample anything completely flat in little time.
78,Rapidash,Fire,,65,100,70,105,80,https://play.pokemonshowdown.com/sprites/bwani/rapidash.gif,https://play.pokemonshowdown.com/sprites/bw/rapidash.png,"Very competitive, this Pokemon will chase anything that moves fast in the hopes of racing it."
79,Slowpoke,Water,Psychic,90,65,65,15,40,https://play.pokemonshowdown.com/sprites/bwani/slowpoke.gif,https://play.pokemonshowdown.com/sprites/bw/slowpoke.png,Incredibly slow and dopey. It takes 5 seconds for it to feel pain when under attack.
80,Slowbro,Water,Psychic,95,75,110,30,80,https://play.pokemonshowdown.com/sprites/bwani/slowbro.gif,https://play.pokemonshowdown.com/sprites/bw/slowbro.png,The SHELLDER that is latched onto SLOWPOKE's tail is said to feed on the host's left over scraps.
81,Magnemite,Electric,,25,35,70,45,95,https://play.pokemonshowdown.com/sprites/bwani/magnemite.gif,https://play.pokemonshowdown.com/sprites/bw/magnemite.png,Uses anti-gravity to stay suspended. Appears without warning and uses THUNDER WAVE and similar moves.
82,Magneton,Electric,,50,60,95,70,120,https://play.pokemonshowdown.com/sprites/bwani/magneton.gif,https://play.pokemonshowdown.com/sprites/bw/magneton.png,Formed by several MAGNEMITEs linked together. They frequently appear when sunspots flare up.
83,Farfetchd,Normal,Flying,52,65,55,60,58,http://play.pokemonshowdown.com/sprites/bwani/farfetchd.gif,https://play.pokemonshowdown.com/sprites/bw/farfetchd.png,The sprig of green onions it holds is its weapon. It is used much like a metal sword.
84,Doduo,Normal,Flying,35,85,45,75,35,https://play.pokemonshowdown.com/sprites/bwani/doduo.gif,https://play.pokemonshowdown.com/sprites/bw/doduo.png,A bird that makes up for its poor flying with its fast foot speed. Leaves giant footprints.
85,Dodrio,Normal,Flying,60,110,70,100,60,https://play.pokemonshowdown.com/sprites/bwani/dodrio.gif,https://play.pokemonshowdown.com/sprites/bw/dodrio.png,"Uses its three brains to execute complex plans. While two heads sleep, one head stays awake."
86,Seel,Water,,65,45,55,45,70,https://play.pokemonshowdown.com/sprites/bwani/seel.gif,https://play.pokemonshowdown.com/sprites/bw/seel.png,The protruding horn on its head is very hard. It is used for bashing through thick ice.
87,Dewgong,Water,Ice,90,70,80,70,95,https://play.pokemonshowdown.com/sprites/bwani/dewgong.gif,https://play.pokemonshowdown.com/sprites/bw/dewgong.png,Stores thermal energy in its body. Swims at a steady 8 knots even in intensely cold waters.
88,Grimer,Poison,,80,80,50,25,40,https://play.pokemonshowdown.com/sprites/bwani/grimer.gif,https://play.pokemonshowdown.com/sprites/bw/grimer.png,Appears in filthy areas. Thrives by sucking up polluted sludge that is pumped out of factories.
89,Muk,Poison,,105,105,75,50,65,https://play.pokemonshowdown.com/sprites/bwani/muk.gif,https://play.pokemonshowdown.com/sprites/bw/muk.png,"Thickly covered with a filthy, vile sludge. It is so toxic, even its footprints contain poison."
90,Shellder,Water,,30,65,100,40,45,https://play.pokemonshowdown.com/sprites/bwani/shellder.gif,https://play.pokemonshowdown.com/sprites/bw/shellder.png,Its hard shell repels any kind of attack. It is vulnerable only when its shell is open.
91,Cloyster,Water,Ice,50,95,180,70,85,https://play.pokemonshowdown.com/sprites/bwani/cloyster.gif,https://play.pokemonshowdown.com/sprites/bw/cloyster.png,"When attacked, it launches its horns in quick volleys. Its innards have never been seen."
92,Gastly,Ghost,Poison,30,35,30,80,100,https://play.pokemonshowdown.com/sprites/bwani/gastly.gif,https://play.pokemonshowdown.com/sprites/bw/gastly.png,"Almost invisible, this gaseous Pokemon cloaks the target and puts it to sleep without notice."
93,Haunter,Ghost,Poison,45,50,45,95,115,https://play.pokemonshowdown.com/sprites/bwani/haunter.gif,https://play.pokemonshowdown.com/sprites/bw/haunter.png,"Because of its ability to slip through block walls, it is said to be from another dimension."
94,Gengar,Ghost,Poison,60,65,60,110,130,https://play.pokemonshowdown.com/sprites/bwani/gengar.gif,https://play.pokemonshowdown.com/sprites/bw/gengar.png,"Under a full moon, this Pokemon likes to mimic the shadows of people and laugh at their fright."
95,Onix,Rock,Ground,35,45,160,70,30,https://play.pokemonshowdown.com/sprites/bwani/onix.gif,https://play.pokemonshowdown.com/sprites/bw/onix.png,"As it grows, the stone portions of its body harden to become similar to a diamond, but colored black."
96,Drowzee,Psychic,,60,48,45,42,90,https://play.pokemonshowdown.com/sprites/bwani/drowzee.gif,https://play.pokemonshowdown.com/sprites/bw/drowzee.png,Puts enemies to sleep then eats their dreams. Occasionally gets sick from eating bad dreams.
97,Hypno,Psychic,,85,73,70,67,115,https://play.pokemonshowdown.com/sprites/bwani/hypno.gif,https://play.pokemonshowdown.com/sprites/bw/hypno.png,"When it locks eyes with an enemy, it will use a mix of PSI moves such as HYPNOSIS and CONFUSION."
98,Krabby,Water,,30,105,90,50,25,https://play.pokemonshowdown.com/sprites/bwani/krabby.gif,https://play.pokemonshowdown.com/sprites/bw/krabby.png,"Its pincers are not only powerful weapons, they are used for balance when walking sideways."
99,Kingler,Water,,55,130,115,75,50,https://play.pokemonshowdown.com/sprites/bwani/kingler.gif,https://play.pokemonshowdown.com/sprites/bw/kingler.png,"The large pincer has 10000 hp of crushing power. However, its huge size makes it unwieldy to use."
100,Voltorb,Electric,,40,30,50,100,55,https://play.pokemonshowdown.com/sprites/bwani/voltorb.gif,https://play.pokemonshowdown.com/sprites/bw/voltorb.png,"Usually found in power plants. Easily mistaken for a Pokeball, they have zapped many people."
101,Electrode,Electric,,60,50,70,140,80,https://play.pokemonshowdown.com/sprites/bwani/electrode.gif,https://play.pokemonshowdown.com/sprites/bw/electrode.png,It stores electric energy under very high pressure. It often explodes with little or no provocation.
102,Exeggcute,Grass,Psychic,60,40,80,40,60,https://play.pokemonshowdown.com/sprites/bwani/exeggcute.gif,https://play.pokemonshowdown.com/sprites/bw/exeggcute.png,"Often mistaken for eggs. When disturbed, they quickly gather and attack in swarms."
103,Exeggutor,Grass,Psychic,95,95,85,55,125,https://play.pokemonshowdown.com/sprites/bwani/exeggutor.gif,https://play.pokemonshowdown.com/sprites/bw/exeggutor.png,"Legend has it that on rare occasions, one of its heads will drop off and continue on as an EXEGGCUTE."
104,Cubone,Ground,,50,50,95,35,40,https://play.pokemonshowdown.com/sprites/bwani/cubone.gif,https://play.pokemonshowdown.com/sprites/bw/cubone.png,"Because it never removes its skull helmet, no one has ever seen this Pokemon's real face."
105,Marowak,Ground,,60,80,110,45,50,https://play.pokemonshowdown.com/sprites/bwani/marowak.gif,https://play.pokemonshowdown.com/sprites/bw/marowak.png,The bone it holds is its key weapon. It throws the bone skillfully like a boomerang to KO targets.
106,Hitmonlee,Fighting,,50,120,53,87,35,https://play.pokemonshowdown.com/sprites/bwani/hitmonlee.gif,https://play.pokemonshowdown.com/sprites/bw/hitmonlee.png,"When in a hurry, its legs lengthen progressively. It runs smoothly with extra long, loping strides."
107,Hitmonchan,Fighting,,50,105,79,76,35,https://play.pokemonshowdown.com/sprites/bwani/hitmonchan.gif,https://play.pokemonshowdown.com/sprites/bw/hitmonchan.png,"While apparently doing nothing, it fires punches in lightning fast volleys that are impossible to see."
108,Lickitung,Normal,,90,55,75,30,60,https://play.pokemonshowdown.com/sprites/bwani/lickitung.gif,https://play.pokemonshowdown.com/sprites/bw/lickitung.png,Its tongue can be extended like a chameleon's. It leaves a tingling sensation when it licks enemies.
109,Koffing,Poison,,40,65,95,35,60,https://play.pokemonshowdown.com/sprites/bwani/koffing.gif,https://play.pokemonshowdown.com/sprites/bw/koffing.png,"Because it stores several kinds of toxic gases in its body, it is prone to exploding without warning."
110,Weezing,Poison,,65,90,120,60,85,https://play.pokemonshowdown.com/sprites/bwani/weezing.gif,https://play.pokemonshowdown.com/sprites/bw/weezing.png,"Where two kinds of poison gases meet, 2 KOFFINGs can fuse into a WEEZING over many years."
111,Rhyhorn,Ground,Rock,80,85,95,25,30,https://play.pokemonshowdown.com/sprites/bwani/rhyhorn.gif,https://play.pokemonshowdown.com/sprites/bw/rhyhorn.png,Its massive bones are 1000 times harder than human bones. It can easily knock a trailer flying.
112,Rhydon,Ground,Rock,105,130,120,40,45,https://play.pokemonshowdown.com/sprites/bwani/rhydon.gif,https://play.pokemonshowdown.com/sprites/bw/rhydon.png,"Protected by an armor-like hide, it is capable of living in molten lava of 3,600 degrees."
113,Chansey,Normal,,250,5,5,50,105,https://play.pokemonshowdown.com/sprites/bwani/chansey.gif,https://play.pokemonshowdown.com/sprites/bw/chansey.png,A rare and elusive Pokemon that is said to bring happiness to those who manage to get it.
114,Tangela,Grass,,65,55,115,60,100,https://play.pokemonshowdown.com/sprites/bwani/tangela.gif,https://play.pokemonshowdown.com/sprites/bw/tangela.png,The whole body is swathed with wide vines that are similar to seaweed. Its vines shake as it walks.
115,Kangaskhan,Normal,,105,95,80,90,40,https://play.pokemonshowdown.com/sprites/bwani/kangaskhan.gif,https://play.pokemonshowdown.com/sprites/bw/kangaskhan.png,The infant rarely ventures out of its mother's protective pouch until it is 3 years old.
116,Horsea,Water,,30,40,70,60,70,https://play.pokemonshowdown.com/sprites/bwani/horsea.gif,https://play.pokemonshowdown.com/sprites/bw/horsea.png,Known to shoot down flying bugs with precision blasts of ink from the surface of the water.
117,Seadra,Water,,55,65,95,85,95,https://play.pokemonshowdown.com/sprites/bwani/seadra.gif,https://play.pokemonshowdown.com/sprites/bw/seadra.png,Capable of swimming backwards by rapidly flapping its wing-like pectoral fins and stout tail.
118,Goldeen,Water,,45,67,60,63,50,https://play.pokemonshowdown.com/sprites/bwani/goldeen.gif,https://play.pokemonshowdown.com/sprites/bw/goldeen.png,"Its tail fin billows like an elegant ballroom dress, giving it the nickname of the Water Queen."
119,Seaking,Water,,80,92,65,68,80,https://play.pokemonshowdown.com/sprites/bwani/seaking.gif,https://play.pokemonshowdown.com/sprites/bw/seaking.png,"In the autumn spawning season, they can be seen swimming powerfully up rivers and creeks."
120,Staryu,Water,,30,45,55,85,70,https://play.pokemonshowdown.com/sprites/bwani/staryu.gif,https://play.pokemonshowdown.com/sprites/bw/staryu.png,An enigmatic Pokemon that can effortlessly regenerate any appendage it loses in battle.
121,Starmie,Water,Psychic,60,75,85,115,100,https://play.pokemonshowdown.com/sprites/bwani/starmie.gif,https://play.pokemonshowdown.com/sprites/bw/starmie.png,Its central core glows with the seven colors of the rainbow. Some people value the core as a gem.
122,MrMime,Psychic,,40,45,65,90,100,http://play.pokemonshowdown.com/sprites/bwani/mrmime.gif,https://play.pokemonshowdown.com/sprites/bw/mrmime.png,"If interrupted while it is miming, it will slap around the offender with its broad hands."
123,Scyther,Bug,Flying,70,110,80,105,55,https://play.pokemonshowdown.com/sprites/bwani/scyther.gif,https://play.pokemonshowdown.com/sprites/bw/scyther.png,"With ninja-like agility and speed, it can create the illusion that there is more than one."
124,Jynx,Ice,Psychic,65,50,35,95,95,https://play.pokemonshowdown.com/sprites/bwani/jynx.gif,https://play.pokemonshowdown.com/sprites/bw/jynx.png,It seductively wiggles its hips as it walks. It can cause people to dance in unison with it.
125,Electabuzz,Electric,,65,83,57,105,85,https://play.pokemonshowdown.com/sprites/bwani/electabuzz.gif,https://play.pokemonshowdown.com/sprites/bw/electabuzz.png,"Normally found near power plants, they can wander away and cause major blackouts in cities."
126,Magmar,Fire,,65,95,57,93,85,https://play.pokemonshowdown.com/sprites/bwani/magmar.gif,https://play.pokemonshowdown.com/sprites/bw/magmar.png,Its body always burns with an orange glow that enables it to hide perfectly among flames.
127,Pinsir,Bug,,65,125,100,85,55,https://play.pokemonshowdown.com/sprites/bwani/pinsir.gif,https://play.pokemonshowdown.com/sprites/bw/pinsir.png,"If it fails to crush the victim in its pincers, it will swing it around and toss it hard."
128,Tauros,Normal,,75,100,95,110,70,https://play.pokemonshowdown.com/sprites/bwani/tauros.gif,https://play.pokemonshowdown.com/sprites/bw/tauros.png,"When it targets an enemy, it charges furiously while whipping its body with its long tails."
129,Magikarp,Water,,20,10,55,80,20,https://play.pokemonshowdown.com/sprites/bwani/magikarp.gif,https://play.pokemonshowdown.com/sprites/bw/magikarp.png,"In the distant past, it was somewhat stronger than the horribly weak descendants that exist today."
130,Gyarados,Water,Flying,95,125,79,81,100,https://play.pokemonshowdown.com/sprites/bwani/gyarados.gif,https://play.pokemonshowdown.com/sprites/bw/gyarados.png,"Rarely seen in the wild. Huge and vicious, it is capable of destroying entire cities in a rage."
131,Lapras,Water,Ice,130,85,80,60,95,https://play.pokemonshowdown.com/sprites/bwani/lapras.gif,https://play.pokemonshowdown.com/sprites/bw/lapras.png,A Pokemon that has been overhunted almost to extinction. It can ferry people across the water.
132,Ditto,Normal,,48,48,48,48,48,https://play.pokemonshowdown.com/sprites/bwani/ditto.gif,https://play.pokemonshowdown.com/sprites/bw/ditto.png,Capable of copying an enemy's genetic code to instantly transform itself into a duplicate of the enemy.
133,Eevee,Normal,,55,55,50,55,65,https://play.pokemonshowdown.com/sprites/bwani/eevee.gif,https://play.pokemonshowdown.com/sprites/bw/eevee.png,Its genetic code is irregular. It may mutate if it is exposed to radiation from element STONEs.
134,Vaporeon,Water,,130,65,60,65,110,https://play.pokemonshowdown.com/sprites/bwani/vaporeon.gif,https://play.pokemonshowdown.com/sprites/bw/vaporeon.png,Lives close to water. Its long tail is ridged with a fin which is often mistaken for a mermaid's.
135,Jolteon,Electric,,65,65,60,130,110,https://play.pokemonshowdown.com/sprites/bwani/jolteon.gif,https://play.pokemonshowdown.com/sprites/bw/jolteon.png,It accumulates negative ions in the atmosphere to blast out 10000- volt lightning bolts.
136,Flareon,Fire,,65,130,60,65,110,https://play.pokemonshowdown.com/sprites/bwani/flareon.gif,https://play.pokemonshowdown.com/sprites/bw/flareon.png,"When storing thermal energy in its body, its temperature could soar to over 1600 degrees."
137,Porygon,Normal,,65,60,70,40,75,https://play.pokemonshowdown.com/sprites/bwani/porygon.gif,https://play.pokemonshowdown.com/sprites/bw/porygon.png,A Pokemon that consists entirely of programming code. Capable of moving freely in cyberspace.
138,Omanyte,Rock,Water,35,40,100,35,90,https://play.pokemonshowdown.com/sprites/bwani/omanyte.gif,https://play.pokemonshowdown.com/sprites/bw/omanyte.png,"Although long extinct, in rare cases, it can be genetically resurrected from fossils."
139,Omastar,Rock,Water,70,60,125,55,115,https://play.pokemonshowdown.com/sprites/bwani/omastar.gif,https://play.pokemonshowdown.com/sprites/bw/omastar.png,A prehistoric Pokemon that died out when its heavy shell made it impossible to catch prey.
140,Kabuto,Rock,Water,30,80,90,55,45,https://play.pokemonshowdown.com/sprites/bwani/kabuto.gif,https://play.pokemonshowdown.com/sprites/bw/kabuto.png,A Pokemon that was resurrected from a fossil found in what was once the ocean floor eons ago.
141,Kabutops,Rock,Water,60,115,105,80,70,https://play.pokemonshowdown.com/sprites/bwani/kabutops.gif,https://play.pokemonshowdown.com/sprites/bw/kabutops.png,Its sleek shape is perfect for swimming. It slashes prey with its claws and drains the body fluids.
142,Aerodactyl,Rock,Flying,80,105,65,130,60,https://play.pokemonshowdown.com/sprites/bwani/aerodactyl.gif,https://play.pokemonshowdown.com/sprites/bw/aerodactyl.png,"A ferocious, prehistoric Pokemon that goes for the enemy's throat with its serrated saw-like fangs."
143,Snorlax,Normal,,160,110,65,30,65,https://play.pokemonshowdown.com/sprites/bwani/snorlax.gif,https://play.pokemonshowdown.com/sprites/bw/snorlax.png,"Very lazy. Just eats and sleeps. As its rotund bulk builds, it becomes steadily more slothful."
144,Articuno,Ice,Flying,90,85,100,85,125,https://play.pokemonshowdown.com/sprites/bwani/articuno.gif,https://play.pokemonshowdown.com/sprites/bw/articuno.png,A legendary bird Pokemon that is said to appear to doomed people who are lost in icy mountains.
145,Zapdos,Electric,Flying,90,90,85,100,125,https://play.pokemonshowdown.com/sprites/bwani/zapdos.gif,https://play.pokemonshowdown.com/sprites/bw/zapdos.png,A legendary bird Pokemon that is said to appear from clouds while dropping enormous lightning bolts.
146,Moltres,Fire,Flying,90,100,90,90,125,https://play.pokemonshowdown.com/sprites/bwani/moltres.gif,https://play.pokemonshowdown.com/sprites/bw/moltres.png,Known as the legendary bird of fire. Every flap of its wings creates a dazzling flash of flames.
147,Dratini,Dragon,,41,64,45,50,50,https://play.pokemonshowdown.com/sprites/bwani/dratini.gif,https://play.pokemonshowdown.com/sprites/bw/dratini.png,Long considered a mythical Pokemon until recently when a small colony was found living underwater.
148,Dragonair,Dragon,,61,84,65,70,70,https://play.pokemonshowdown.com/sprites/bwani/dragonair.gif,https://play.pokemonshowdown.com/sprites/bw/dragonair.png,A mystical Pokemon that exudes a gentle aura. Has the ability to change climate conditions.
149,Dragonite,Dragon,Flying,91,134,95,80,100,https://play.pokemonshowdown.com/sprites/bwani/dragonite.gif,https://play.pokemonshowdown.com/sprites/bw/dragonite.png,An extremely rarely seen marine Pokemon. Its intelligence is said to match that of humans.
150,Mewtwo,Psychic,,106,110,90,130,154,https://play.pokemonshowdown.com/sprites/bwani/mewtwo.gif,https://play.pokemonshowdown.com/sprites/bw/mewtwo.png,It was created by a scientist after years of horrific gene splicing and DNA engineering experiments.
151,Mew,Psychic,,100,100,100,100,100,https://play.pokemonshowdown.com/sprites/bwani/mew.gif,https://play.pokemonshowdown.com/sprites/bw/mew.png,So rare that it is still said to be a mirage by many experts. Only a few people have seen it worldwide.""")
data_pokes = pd.read_csv(rawdata, sep=',')

data_pokes = data_pokes.set_index('Pokemon', drop=False)

initial_constraints = pd.DataFrame(columns=['LEFT HAND SIDE', 'SIGN', 'RIGHT HAND SIDE'],
                                   data=[['# OF POKEMON', '>=', '1'],
                                         ['# OF POKEMON', '<=', '6'],
                                         ['', '', ''], ['', '', ''],
                                         ['', '', ''], ['', '', '']
                                        ],
                                   index=['a','b','c','d','e','f'])

# add total stat
data_pokes['Total'] = data_pokes.HP + data_pokes.ATTACK + data_pokes.DEFENSE + data_pokes.SPEED + data_pokes.SPECIAL

# create list of unique pokemon, types, and statss
pokes = data_pokes.Pokemon
data_pokes['Type 1'] = data_pokes['Type 1'].str.upper()
data_pokes['Type 2'] = data_pokes['Type 2'].str.upper()
poke_types = pd.unique(data_pokes[['Type 1', 'Type 2']].values.ravel('K'))
poke_types = poke_types[~pd.isnull(poke_types)]
poke_stats = ['HP', 'ATTACK', 'DEFENSE', 'SPEED', 'SPECIAL']

# poke stats parameters
param_stats = {(p,s): data_pokes.get_value(p,s) for p in pokes for s in poke_stats}

# poke types parameters (1 hot encode the types)
type_1_dummies = pd.get_dummies(data_pokes['Type 1'])
type_2_dummies = pd.get_dummies(data_pokes['Type 2'])
for t in poke_types:
    if t not in list(type_1_dummies):
        type_1_dummies[t] = 0
    if t not in list(type_2_dummies):
        type_2_dummies[t] = 0 
type_1_dummies = type_1_dummies.sort_index(axis=1)
type_2_dummies = type_2_dummies.sort_index(axis=1)
type_dummies = pd.concat([type_1_dummies, type_2_dummies]).max(level=0)
param_types = {(p,t): type_dummies.get_value(p,t) for p in pokes for t in poke_types}
   
# decision variables
x_vars  = {p: plp.LpVariable(cat=plp.LpInteger, lowBound=0, upBound=1, name="x_{0}".format(p)) for p in pokes}

##########################################
# DASH app
##########################################

# constants
url_pokeball = 'https://lh6.googleusercontent.com/-7ze4Lb2iiOI/UptLoxXERxI/AAAAAAAAAEM/T0RV2S4bAgs/s145-p/pokeball-sprite-150-150.png'


app = dash.Dash(__name__, static_folder='assets')
server = app.server

app.layout = html.Div(id = 'full_page', children=[
    html.Table(children=[
        html.Tr(children=[html.Td(children=[html.H1(children='PokePULP', className='page_Title')], colSpan='6')]),
    
        # objective section
        html.Tr(children=[
            html.Td(children=[
                html.Table(id='obj_table', children=[
                    html.Tr(children=[
                        html.Td(children=html.Div(children='Objective', className='section_Heading'), style={'width': '200px'}),
                        html.Td(colSpan='1', style={'width': '200px'}),
                        html.Td(colSpan='1', style={'width': '200px'}),
                        html.Td(colSpan='1', style={'width': '200px'})]),
                    html.Tr(children=[
                        html.Td(children=[
                            dcc.Dropdown(id='dd_obj_type', clearable=False, value='MAXIMIZE', style={'width': '180px'},
                                         options=[{'label': 'MAXIMIZE', 'value': 'MAXIMIZE'},{'label': 'MINIMIZE', 'value': 'MINIMIZE'}])], 
                            colSpan='1'),
                        html.Td(children=[html.Button('UPDATE OBJECTIVE', id='btn_update_objective')], 
                            colSpan='1'),
                        html.Td(id='obj_function_equals', children='Objective Function = ', colSpan='1'),
                        html.Td(children=[html.Div(id='div_objective', children='MAXIMIZE TOTAL HP')], colSpan='1')]),
                    html.Tr(children=[
                            html.Td(children=[dcc.Dropdown(id='dd_obj_func', clearable=False, value='TOTAL HP', style={'width': '180px'},
                                         options=[{'label': 'TOTAL HP', 'value': 'TOTAL HP'},
                                                  {'label': 'TOTAL ATTACK', 'value': 'TOTAL ATTACK'},
                                                  {'label': 'TOTAL DEFENSE', 'value': 'TOTAL DEFENSE'},
                                                  {'label': 'TOTAL SPEED', 'value': 'TOTAL SPEED'},
                                                  {'label': 'TOTAL SPECIAL', 'value': 'TOTAL SPECIAL'}])], colSpan='1'),
                            html.Td(children=[], colSpan='1'),
                            html.Td(id='obj_value_equals', children=['Objective Value = '], colSpan='1'),
                            html.Td(children=[html.Div(id='div_obj_value')], colSpan='1')])])],
                    colSpan='4', rowSpan='1', style={'width': '800px'}),
             html.Td(children=[
                     html.Table(id='tbl_pokes', children=[
                             html.Tr(children=[
                                     html.Td(children=html.Img(id='img_poke_1', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_2', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_3', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_4', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_5', src=url_pokeball, width=50, height=50)),
                                     html.Td(children=html.Img(id='img_poke_6', src=url_pokeball, width=50, height=50))
                                     ]),
                            html.Tr(children=[
                                    html.Td(id='txt_poke_1', className='name_text', children=''),
                                    html.Td(id='txt_poke_2', className='name_text', children=''),
                                    html.Td(id='txt_poke_3', className='name_text', children=''),
                                    html.Td(id='txt_poke_4', className='name_text', children=''),
                                    html.Td(id='txt_poke_5', className='name_text', children=''),
                                    html.Td(id='txt_poke_6', className='name_text', children='')
                                    ])
                             ])],
                    colSpan='2', rowSpan='1')]),
        html.Tr(children=['']),
    

        # constraints section
        html.Tr(children=[
            html.Td(children=[
                html.Table(id='const_table',
                    children=[
                    html.Tr(children=[
                        html.Td(children='Constraints', className='section_Heading'), 
                        html.Td(colSpan='3')]),
                    html.Tr(children=[
                        html.Td(children=[
                            dcc.Dropdown(id='dd_const_type', clearable=False, value='TEAM SIZE',
                                options=[{'label': 'TEAM SIZE', 'value': 'TEAM SIZE'},
                                         {'label': 'STATS', 'value': 'STATS'},
                                         {'label': 'POKE TYPES', 'value': 'POKE TYPES'}],
                                style={'width': '180px'})]),
                        html.Td(children=[
                            html.Div(children=[
                               DataTable(id='dt_constraints', sortable=False, editable=False, rows=[{}],
                                   row_selectable=True, columns=['LEFT HAND SIDE','SIGN','RIGHT HAND SIDE'])],
                               style={'width': '600px', 'display': 'inline-block'})],
                            rowSpan='6', colSpan='3')]),
                    html.Tr(children=[
                        html.Td(children=dcc.Dropdown(id='dd_const_lhs', clearable=False, value='# OF POKEMON', style={'width': '180px'},
                                  options=[{'label': '# OF POKEMON', 'value': '# OF POKEMON'}]))]),
                    html.Tr(children=[
                        html.Td(children=dcc.Dropdown(id = 'dd_const_sign', clearable=False, value='<=', style={'width': '180px'},
                     options=[{'label': '≤', 'value': '<='},{'label': '≥', 'value': '>='}]))]),
                    html.Tr(children=[
                        html.Td(children=dcc.Input(id='txtbox_const_rhs', placeholder='',type='number', value=0, max=9999, min=0, style={'width': '180px'}))]),
                    html.Tr(children=[
                        html.Td(html.Button('ADD CONSTRAINT', id='btn_add_constraint'))]),
                    html.Tr(children=
                        [html.Td(html.Button('REMOVE CONSTRAINT', id='btn_remove_constraint', style={'background-color': 'lightgray'}))])])],
                colSpan='4', rowSpan='7', style={'width': '800px'}),
    
            # stats graph
            html.Td(children= dcc.Graph(id='graph_team_stats',
                        figure={'data': [{'x': ['HP', 'Attack', 'Defense', 'Speed', 'Special'], 'y': [0, 0, 0, 0, 0], 'type': 'bar'}],
                               'layout': {'plot_bgcolor': 'white', 'paper_bgcolor': 'WhiteSmoke', 'font': {'color': 'black'},
                                          'margin': {'l': 25, 'b': 20, 't': 25, 'r': 5}, 'showlegend':False, 'title':'Team Stats',
                                          'yaxis': {'range': [0, 100]}}},
                        style={'width': 300, 'height':300},
                        config={'displayModeBar': False}),
                    colSpan='2', rowSpan='7')]),
        html.Tr(),
        html.Tr(),
        html.Tr(),
        html.Tr(),
        html.Tr(),
        html.Tr(),      
        html.Tr(children=[
            html.Td(colSpan='1'),
            html.Td(colSpan='3'),
            html.Td(colSpan='1'),
            html.Td(colSpan='1')]),
        html.Tr(children=[
            html.Td(children=[
                html.Table(id='controls_table', children=[
                    html.Tr(children=[
                        html.Td(children=html.Button('SOLVE!', id='btn_solve'), rowSpan='2', style={'width': '200px'}),
                        html.Td(id='problem_status', children='Problem Status:', style={'width': '200px'}),
                        html.Td(id='message', children='Message:', style={'width': '400px'}, colSpan='2')]),     
                    html.Tr(children=[
                        html.Td(children=[html.Div(id='div_obj_status', children='obj status........')]),
                        html.Td(children=[html.Div(id='div_message', children='Welcome to PokePulp! Set up your optimization problem and then click SOLVE!')], colSpan='2')])], style={'height': '70px'})],
                colSpan='4', style={'width': '800px'}),
            html.Td(colSpan='3')])]),
    
        # STORAGE  ############  
        dcc.Store(id='opt_results'),
        dcc.Store(id='const_df')],
    style={'width': 1250})
    
    
# update objective function when user presses Update Objective
@app.callback(
    Output('div_objective', 'children'),
    [Input('btn_update_objective', 'n_clicks_timestamp')],
    [State('dd_obj_type', 'value'),
     State('dd_obj_func', 'value')])
def update_objective_function(btn_obj_ncts, obj_type, obj_stat):
    # split objective column into two words
    obj_string = obj_type + ' ' + obj_stat
    return(obj_string)
    
# update the constraint LHS options when the user
# changes the selected constraint type
@app.callback(
    Output('dd_const_lhs', 'options'),
    [Input('dd_const_type', 'value')])
def update_dd_const_lhs_choices(const_type):
    if const_type == 'TEAM SIZE':
        dd_const_lhs_options = [{'label': '# OF POKEMON', 'value': '# OF POKEMON'}]
    if const_type == 'STATS':
        dd_const_lhs_options = [{'label': 'TOTAL HP', 'value': 'TOTAL HP'},
                             {'label': 'TOTAL ATTACK', 'value': 'TOTAL ATTACK'},
                             {'label': 'TOTAL DEFENSE', 'value': 'TOTAL DEFENSE'},
                             {'label': 'TOTAL SPEED', 'value': 'TOTAL SPEED'},
                             {'label': 'TOTAL SPECIAL', 'value': 'TOTAL SPECIAL'}]
    if const_type == 'POKE TYPES':
        dd_const_lhs_options = [{'label': '# OF BUG TYPES', 'value': '# OF BUG TYPES'},
                             {'label': '# OF DRAGON TYPES', 'value': '# OF DRAGON TYPES'},
                             {'label': '# OF ELECTRIC TYPES', 'value': '# OF ELECTRIC TYPES'},
                             {'label': '# OF FIGHTING TYPES', 'value': '# OF FIGHTING TYPES'},
                             {'label': '# OF FIRE TYPES', 'value': '# OF FIRE TYPES'},
                             {'label': '# OF FLYING TYPES', 'value': '# OF FLYING TYPES'},
                             {'label': '# OF GHOST TYPES', 'value': '# OF GHOST TYPES'},
                             {'label': '# OF GRASS TYPES', 'value': '# OF GRASS TYPES'},
                             {'label': '# OF GROUND TYPES', 'value': '# OF GROUND TYPES'},
                             {'label': '# OF ICE TYPES', 'value': '# OF ICE TYPES'},
                             {'label': '# OF NORMAL TYPES', 'value': '# OF NORMAL TYPES'},
                             {'label': '# OF POISON TYPES', 'value': '# OF POISON TYPES'},
                             {'label': '# OF PSYCHIC TYPES', 'value': '# OF PSYCHIC TYPES'},
                             {'label': '# OF ROCK TYPES', 'value': '# OF ROCK TYPES'},
                             {'label': '# OF WATER TYPES', 'value': '# OF WATER TYPES'}]
    return(dd_const_lhs_options)

# change the selected constraint LHS value when the user
# changes the selected constraint type
@app.callback(
    Output('dd_const_lhs', 'value'),
    [Input('dd_const_type', 'value')])
def update_dd_const_lhs_value(const_type):
    if const_type == 'TEAM SIZE':
        dd_const_lhs_value = '# OF POKEMON'
    if const_type == 'STATS':
        dd_const_lhs_value = 'TOTAL HP'
    if const_type == 'POKE TYPES':
        dd_const_lhs_value = '# OF BUG TYPES'
    return(dd_const_lhs_value)

# add/remove a constraint when the respective button is clicked 
@app.callback(
    Output('const_df', 'data'),
    [Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp')],
    [State('const_df', 'data'), State('dd_const_lhs', 'value'),
     State('dd_const_sign', 'value'), State('txtbox_const_rhs', 'value'),
     State('dt_constraints', 'selected_row_indices')])
def add_constraint(btn_add_ncts, btn_rem_ncts, const_df, my_lhs, my_sign, my_rhs, selected_rows):
    const_df = pd.DataFrame.from_dict(const_df)
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    # check which button was clicked most recently (based on time stamp)
    if int(btn_add_ncts) > int(btn_rem_ncts): 
        if btn_add_ncts is not None and good_rhs(my_rhs):
            new_const_df = pd.DataFrame(columns=['LEFT HAND SIDE', 'SIGN', 'RIGHT HAND SIDE'], data=[[my_lhs, my_sign, my_rhs]], index=['g'])
            const_df = const_df.append(new_const_df, ignore_index=False)
            blank_row_indices = const_df[const_df.SIGN==''].index.values
            const_df = const_df.drop(sorted(blank_row_indices)[-1])
            const_df = sort_constraints(const_df)
        else:
            const_df = initial_constraints
    elif int(btn_rem_ncts) > int(btn_add_ncts):
        selected_rows = [s for s in selected_rows if s > 1]
        const_df = const_df.drop(const_df.index[selected_rows])
        new_const_df = pd.DataFrame(columns=['LEFT HAND SIDE', 'SIGN', 'RIGHT HAND SIDE'], data=[['', '', '']])
        for r in selected_rows:
            const_df = const_df.append(new_const_df, ignore_index=True)
        const_df = sort_constraints(const_df)
    else:
        const_df = initial_constraints
    output = const_df.to_dict()
    return output


# update the constraints shown in the datatable whenever
# the user changes them
@app.callback(
    Output('dt_constraints', 'rows'),
    [Input('const_df', 'data')])
def display_constraint_table(const_df):
    const_df = pd.DataFrame.from_dict(const_df)
    return const_df.to_dict('records')

# disable add constraint button when there are 6 constraints
@app.callback(
    Output('btn_add_constraint', 'disabled'),
    [Input('const_df', 'data')])
def disable_add_constraint(const_df):
    const_df = pd.DataFrame.from_dict(const_df)
    const_count = 6 - len(const_df[const_df['LEFT HAND SIDE'] == ''])
    if const_count == 6:
        off = True
    else:
        off = False
    return off

@app.callback(
    Output('btn_add_constraint', 'style'),
    [Input('const_df', 'data')])
def style_btn_add_constraint(const_df):
    const_df = pd.DataFrame.from_dict(const_df)
    const_count = 6 - len(const_df[const_df['LEFT HAND SIDE'] == ''])
    if const_count == 6:
        myStyle = {'background-color': 'lightgray'}
    else:
        myStyle = {'background-color': 'white'}
    return myStyle

# disable remove constraint button if none are selected
@app.callback(
    Output('btn_remove_constraint', 'style'),
    [Input('dt_constraints', 'selected_row_indices')])
def style_btn_remove_constraint(selected_rows):
    if len(selected_rows) == 0:
        myStyle = {'background-color': 'lightgray'}
    else:
        myStyle = {'background-color': 'white'}
    return myStyle

# disable remove constraint button whenever const_df changes
@app.callback(
    Output('dt_constraints', 'selected_row_indices'),
    [Input('const_df', 'data')])
def style_btn_remove_constraint2(myStyle):
    # (I already have a callback for btn_remove_constraint style so I must
    # use this callbback to update df_constraints selected_row_indices which in turn
    # calls the callback for btn_remove_constraint style)
    return []


# solve the optimization problem when the user clicks solve
@app.callback(
    Output('opt_results', 'data'),
    [Input('btn_solve', 'n_clicks')],
    [State('const_df', 'data'),
     State('div_objective', 'children')])
def solve_opt(n_clicks, const_df, obj_function):
    if n_clicks is not None:
        opt_model = plp.LpProblem(name="pokemon_picker")
        opt_model = add_decision_vars(opt_model)
        obj_list = parse_objective(obj_function)
        opt_model = add_objective(opt_model, obj_list[0], obj_list[1])
        const_df = pd.DataFrame.from_dict(const_df)
        opt_model = add_constraints(opt_model, const_df)
        opt_model.solve()
        opt_df = pd.DataFrame(list(x_vars.items()), columns=['Pokemon', 'VarName'])
        opt_df["solution_value"] = opt_df["VarName"].apply(lambda item: item.varValue)
        selected_pokes = opt_df.loc[opt_df.solution_value == 1,'Pokemon']
        obj_val = opt_model.objective.value()
        opt_status = plp.LpStatus[opt_model.status]
        if opt_status != 'Optimal':
            selected_pokes = []
        output = {'poke_list': selected_pokes, 'obj_value': obj_val, 'status': opt_status}
        return(output)
        
def parse_objective(obj_string):
    obj_string_list = obj_string.split()
    obj_type = obj_string_list[0]
    obj_stat = obj_string_list[1] + ' ' + obj_string_list[2]
    return([obj_type, obj_stat])
    
# add decision variables to the optimization model
def add_decision_vars(opt_model):
    for key, value in x_vars.items():
        opt_model += value
    return(opt_model)

# add objective to the optimization model,
# based on user's selections
def add_objective(opt_model, obj_type, obj_func):
    my_obj_stat = list(compress(poke_stats, [s in obj_func for s in poke_stats]))[0]
    my_obj = plp.lpSum(x_vars[p] * param_stats.get((p, my_obj_stat)) for p in pokes)
    if obj_type == 'MAXIMIZE':
        opt_model.sense = plp.LpMaximize
    else:
        opt_model.sense = plp.LpMinimize
    opt_model.setObjective(my_obj)
    return(opt_model)

# add constraints to the optimization model,
# based on user's selections  
def add_constraints(opt_model, const_df):
    const_count = 0
    for index, row in const_df.iterrows():
        const_count += 1
        if row['SIGN'] == '':
            continue
        elif row['SIGN'] == '<=': 
            const_sign = plp.LpConstraintLE
        else:
            const_sign = plp.LpConstraintGE
        if row['LEFT HAND SIDE'] == '# OF POKEMON':
            new_const = plp.LpConstraint(
                             e=plp.lpSum(x_vars[p] for p in pokes),
                             sense=const_sign,
                             rhs=int(row['RIGHT HAND SIDE']),
                             name="constraint_{0}".format(const_count))
        elif 'TOTAL' in row['LEFT HAND SIDE']:
            my_const_stat = list(compress(poke_stats, [s in row['LEFT HAND SIDE'] for s in poke_stats]))[0]
            new_const = plp.LpConstraint(
                             e=plp.lpSum(x_vars[p] * param_stats.get((p, my_const_stat)) for p in pokes),
                             sense=const_sign,
                             rhs=int(row['RIGHT HAND SIDE']),
                             name="constraint_{0}".format(const_count))
        elif 'TYPE' in row['LEFT HAND SIDE']:
            my_type = list(compress(poke_types, [t in row['LEFT HAND SIDE'] for t in poke_types]))[0]
            new_const = plp.LpConstraint(
                             e=plp.lpSum(x_vars[p] * param_types.get((p, my_type)) for p in pokes),
                             sense=const_sign,
                             rhs=int(row['RIGHT HAND SIDE']),
                             name="constraint_{0}".format(const_count))
        opt_model += new_const
    return(opt_model)

# update poke_1 GIF when optimization model is solved
@app.callback(
    Output('img_poke_1', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_1(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 1:
                my_poke = poke_list[0]
                my_url = data_pokes.loc[my_poke, 'GIF']
    return my_url

# update poke_2 GIF when optimization model is solved
@app.callback(
    Output('img_poke_2', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_2(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 2:
                my_poke = poke_list[1]
                my_url = data_pokes.loc[my_poke, 'GIF']
    return my_url

# update poke_3 GIF when optimization model is solved
@app.callback(
    Output('img_poke_3', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_3(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 3:
                my_poke = poke_list[2]
                my_url = data_pokes.loc[my_poke, 'GIF']
    return my_url

# update poke_4 GIF when optimization model is solved
@app.callback(
    Output('img_poke_4', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_4(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 4:
                my_poke = poke_list[3]
                my_url = data_pokes.loc[my_poke, 'GIF']
    return my_url

# update poke_5 GIF when optimization model is solved
@app.callback(
    Output('img_poke_5', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_5(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 5:
                my_poke = poke_list[4]
                my_url = data_pokes.loc[my_poke, 'GIF']
    return my_url

# update poke_6 GIF when optimization model is solved
@app.callback(
    Output('img_poke_6', 'src'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_poke_6(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_url = url_pokeball
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 6:
                my_poke = poke_list[5]
                my_url = data_pokes.loc[my_poke, 'GIF']
    return my_url

# update poke_1 text when optimization model is solved
@app.callback(
    Output('txt_poke_1', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_1(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 1:
                my_poke = poke_list[0]
    return my_poke

# update poke_2 text when optimization model is solved
@app.callback(
    Output('txt_poke_2', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_2(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 2:
                my_poke = poke_list[1]
    return my_poke

# update poke_3 text when optimization model is solved
@app.callback(
    Output('txt_poke_3', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_3(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 3:
                my_poke = poke_list[2]
    return my_poke

# update poke_4 text when optimization model is solved
@app.callback(
    Output('txt_poke_4', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_4(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 4:
                my_poke = poke_list[3]
    return my_poke

# update poke_5 text when optimization model is solved
@app.callback(
    Output('txt_poke_5', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_5(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 5:
                my_poke = poke_list[4]
    return my_poke

# update poke_6 text when optimization model is solved
@app.callback(
    Output('txt_poke_6', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_txt_6(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    my_poke = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            poke_list = opt_res.get('poke_list')
            if len(poke_list) >= 6:
                my_poke = poke_list[5]
    return my_poke

# show objective value on page when optimization model is solved
@app.callback(
    Output('div_obj_value', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp')])
def show_obj_value(opt_res, btn_add_ncts, btn_rem_ncts, btn_solve_ncts, btn_obj_ncts):
    obj_val = '?'
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            opt_status = opt_res.get('status')
            if opt_status == 'Infeasible':
                return obj_val
            obj_val = opt_res.get('obj_value')
    return obj_val

# show status of optimization model when it is solved
@app.callback(
    Output('div_obj_status', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp')])
def show_obj_status(opt_res, btn_add_ncts, btn_rem_ncts, btn_solve_ncts, btn_obj_ncts):
    opt_status = ''
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            opt_status = opt_res.get('status')
    return opt_status

# update message box when model is solved
@app.callback(
    Output('div_message', 'children'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp')],
     [State('dt_constraints', 'selected_row_indices'),
      State('txtbox_const_rhs', 'value')])
def show_obj_status(opt_res, btn_add_ncts, btn_rem_ncts, btn_solve_ncts, btn_obj_ncts, selected_rows, my_rhs):
    msg = 'Welcome to PokePulp! Set up your optimization problem and then click SOLVE!'
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0 
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):    
        opt_status = opt_res.get('status')
        if opt_status == 'Optimal':
            msg = 'You found the optimal pokemon team!'
        elif opt_status == 'Infeasible':
            msg = 'The problem is infeasible. Try adjusting the constraints and re-solving.'
    else:
        if int(btn_add_ncts) > 0 or int(btn_rem_ncts) > 0 or int(btn_obj_ncts) > 0:
            msg = 'Click SOLVE once you are finished adjusting the model.'
            if int(btn_rem_ncts) > int(btn_add_ncts) and int(btn_rem_ncts) > int(btn_obj_ncts) and min(selected_rows) <= 1:
                msg = 'WARNING: The first two constraints cannot be removed.'
            if int(btn_add_ncts) > int(btn_rem_ncts) and int(btn_add_ncts) > int(btn_obj_ncts) and good_rhs(my_rhs) == False:
                msg = 'WARNING: Constraint RHS value must be an integer >= 0.'
    return msg

# update team stats graph
@app.callback(
    Output('graph_team_stats', 'figure'),
    [Input('opt_results', 'data'),
     Input('btn_add_constraint', 'n_clicks_timestamp'),
     Input('btn_remove_constraint', 'n_clicks_timestamp'),
     Input('btn_update_objective', 'n_clicks_timestamp'),
     Input('btn_solve', 'n_clicks_timestamp')])
def update_team_stats_graph(opt_res, btn_add_ncts, btn_rem_ncts, btn_obj_ncts, btn_solve_ncts):
    graph_default = {'data': [{'x': ['HP', 'Attack', 'Defense', 'Speed', 'Special'], 'y': [0, 0, 0, 0, 0], 'type': 'bar'}],
                     'layout': {'plot_bgcolor': 'white', 'paper_bgcolor': 'WhiteSmoke', 'font': {'color': 'black'},
                                'margin': {'l': 25, 'b': 20, 't': 25, 'r': 5}, 'showlegend':False, 'title':'Team Stats',
                                'yaxis': {'range': [0, 100]}}}
    graph_output = graph_default
    if btn_solve_ncts is None:
        btn_solve_ncts = 0
    if btn_add_ncts is None:
        btn_add_ncts = 0
    if btn_rem_ncts is None:
        btn_rem_ncts = 0
    if btn_obj_ncts is None:
        btn_obj_ncts = 0 
    if int(btn_solve_ncts) > int(btn_rem_ncts) and int(btn_solve_ncts) > int(btn_add_ncts) and int(btn_solve_ncts) > int(btn_obj_ncts):
        if opt_res is not None:
            opt_status = opt_res.get('status')
            if opt_status == 'Optimal':
                poke_list = opt_res.get('poke_list')
                stat_hp = sum([param_stats.get((p, 'HP')) for p in poke_list])
                stat_attack = sum([param_stats.get((p, 'ATTACK')) for p in poke_list])
                stat_defense = sum([param_stats.get((p, 'DEFENSE')) for p in poke_list])
                stat_speed = sum([param_stats.get((p, 'SPEED')) for p in poke_list])
                stat_special = sum([param_stats.get((p, 'SPECIAL')) for p in poke_list])
                graph_output = {'data': [{'x': ['HP', 'Attack', 'Defense', 'Speed', 'Special'], 'y': [stat_hp, stat_attack, stat_defense, stat_speed, stat_special], 'type': 'bar', 'name': 'SF'}],
                                 'layout': {'plot_bgcolor': 'white', 'paper_bgcolor': 'WhiteSmoke', 'font': {'color': 'black'},
                                            'margin': {'l': 25, 'b': 20, 't': 25, 'r': 5}, 'showlegend':False, 'title':'Team Stats'}}
    return graph_output

# helper function to sort constraints df by moving blanks to end
def sort_constraints(constraint_df):
    const_present = constraint_df[constraint_df.SIGN!='']
    const_blank = constraint_df[constraint_df.SIGN=='']
    const_sorted = const_present.append(const_blank, ignore_index=True).reset_index(drop=True)
    const_sorted.index = ['a','b','c','d','e','f']
    return(const_sorted)

# helper function to check if RHS constraint value is ok
def good_rhs(val):
    try: 
        val_int = int(val)
        if val_int >= 0:
            return True
        else:
            return False
    except ValueError:
        return False


if __name__ == '__main__':
    app.run_server(debug=False)

    
    