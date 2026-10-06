# Agent Traveler

* Designed to work with you LLM, to help travelers with their trips,
So the idea is to give an accurate or idea of a trip, and the agentl will help you
to clarify ideas, show you options.

Is not going to schedule or pay the trip, the idea is just to give an accurate report
of the trip, and the user can use it to plan their trip.


The main agent is .agents/agents/travel-supervisor.md, which is going to be the router, who calls other skills (To gain some token reduction) which will be in charge of the main workflow


* .agents/agents/travel-supervisor.md: Agent Router, in charge of the main workflow, so, if you wanna add an additional step, here is the right place. 

* .agents/agents/cancilleria-scanner.md Borders are tricky, we need visas despite of the technology, so this is the agent in charge of checking visas, and border requirements for colombian citizens. Supporting by .agents/skills/cancilleria-country-policy

* .agents/agents/destination-researcher.md Fundamental for the idea of travelling, and the heart of this repo, this agent helps us to stablish a path check how we are going to reach and the path to follow in the trip. Supported by .agents/skills/travel-route-mapping

* .agents/agents/weather-transport-researcher.md Colombia is country with tropical weather, so the weather is not a big factor, just rainy or dry seasson, but arround the world there are different conditions, challenges, problems, according with the time of traveling, could be a dessert or a flood, this agent helps us to check those things, and give us an idea of what to expect.

* .agents/skills/travel-price-scouting, we want to travel anywhere, but the real problem is, the money we have a budget for the trip. This agent check for the best deals around, the best routes and the best time to travel. 
