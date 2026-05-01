---
title: "Essentials - Machines, Creativity & Love - Dr. Lex Fridman"
type: transcript
episode_date: 2025-05-29
episode_number: 295
speakers:
  - Andrew Huberman
  - Lex Fridman
youtube_id: SCzecagKBjY
search:
  exclude: true
---

# Essentials - Machines, Creativity & Love - Dr. Lex Fridman

## [00:00:00] Lex Fridman; Artificial Intelligence (AI), Machine Learning, Deep Learning

**Andrew Huberman:** We meet again. I have a question that I think is on a lot of people's minds or ought to be on a lot of people's minds. What is artificial intelligence and how is it different from things like machine learning and robotics?

**Lex Fridman:** So I think of artificial intelligence first as a big philosophical thing. It's our longing to create other intelligent systems, perhaps systems more powerful than us. At the more narrow level, I think it's also a set of tools — computational mathematical tools to automate different tasks — and also our attempt to understand our own mind. So build systems that exhibit some intelligent behavior in order to understand what intelligence is in our own selves.

**Lex Fridman:** Of course, what AI really means as a community, as a set of researchers and engineers, is a set of computational techniques that allow you to solve various problems. There's a long history of approaches from different perspectives. One thread — one community — goes under the flag of machine learning, which emphasizes the task of learning in the AI space. How do you make a machine that knows very little in the beginning, follows some kind of process, and learns to become better and better at a particular task?

**Lex Fridman:** What's been most effective in the recent fifteen or so years is a set of techniques under the flag of deep learning that utilize neural networks. It's a network of basic computational units called artificial neurons. They have an input and an output, know nothing in the beginning, and are tasked with learning something interesting. There are a lot of ways to break this down, but one dimension is how much human supervision is required to teach the system.

## [00:02:23] Supervised vs Self-Supervised Learning, Self-Play Mechanism

**Lex Fridman:** Supervised learning is when the neural network knows nothing in the beginning and is then given a bunch of labeled examples — in computer vision, that would be images of cats, dogs, cars, traffic signs, each paired with the ground truth of what's in the image. When you have a large database of such examples where you know the truth, the neural network is able to learn by example. One of the fascinating open questions in that space is how do you best represent the truth — a bounding box, semantic segmentation, something else?

**Lex Fridman:** There's a contrasting set of ideas sometimes called unsupervised learning, now more commonly called self-supervised learning, which tries to reduce the need for human annotation. The idea is to let the machine, without any ground truth labels, look at pictures or text on the internet and try to learn something generalizable — what we humans like to call common sense. With self-supervised learning you build this giant base of common sense knowledge on top of which more sophisticated knowledge can be stacked.

**Lex Fridman:** The dream is that you just let an AI system run around the internet for a while, watch millions of hours of YouTube videos, and without any supervision it becomes primed to learn with very few examples once a human shows up — much like human children, whose parents only give one or two examples to teach a concept. A related and weirdly named technique is the self-play mechanism, the engine behind reinforcement learning successes like AlphaGo and AlphaZero, which beat the world champion at chess.

**Lex Fridman:** Self-play is a system that plays against itself — it knows nothing in the beginning, creates mutations of itself, plays those versions, and through this process of interacting with opponents just slightly better than itself, everyone keeps improving. One of the most terrifying and exciting things that David Silver, the creator of AlphaGo and AlphaZero, told me is that they haven't found the ceiling for AlphaZero — it could just arbitrarily keep improving. In chess that doesn't matter much, but the question is what happens if you create that kind of runaway improvement in a domain that has a deeper effect on human societies.

**Andrew Huberman:** And if you inject value alignment — making sure the goals the AI is optimizing for are aligned with human beings and human societies?

**Lex Fridman:** Exactly. To me it's an exciting process if you supervise it correctly. There's a lot to talk about within the specifics of neural networks, but I would say the really big exciting frontier right now is self-supervised learning — we're trying to get less and less human supervision of neural networks.

## [00:09:06] Tesla Autopilot, Autonomous Driving, Robot & Human Interaction

**Lex Fridman:** To me what's exciting is not just the theory — it's the application. One of the most exciting applications of artificial intelligence, specifically neural networks and machine learning, is Tesla Autopilot. These are systems working in the real world with human lives at stake. Even though it's called FSD — Full Self-Driving — it is currently not fully autonomous; human supervision is required, and legally the human is always responsible. That creates a fascinating set of human factors psychology questions.

**Lex Fridman:** What really fascinates me is the whole space of human-robot interaction — when AI systems and humans work together to accomplish tasks. That dance is currently one of the smaller research communities, but I think solving it will be one of the most important open problems going forward. For Elon, semi-autonomous driving is a stepping stone toward fully autonomous driving. He sees humans and robots as unable to dance well together: let humans drive with humans, let robots drive with robots. But I think the world will always be full of problems where humans and robots must interact, because robots will always be flawed, just like humans are.

**Lex Fridman:** The data engine process that Andrej Karpathy, the head of Autopilot, describes is a compelling example of how machine learning works in practice. You build a system that is pretty good, send it out into the real world, it runs into edge cases — failure cases where it screws up. Those edge cases are collected, fed back to the training system, and the next version is improved. You send out a clever AI, let it find the edge cases, and then go back and learn from them, over and over.

**Lex Fridman:** One of the fascinating things about humans is we figure out objective functions for ourselves — that's the meaning of life. A machine currently has to have a hard-coded objective: it must be given very clear statements of what "doing well" means. That's one of the core challenges of AI. You have to formalize the problem, specify the sensory inputs, and specify the goal you're trying to reach. Now, you could argue humans also have objective functions we're optimizing — we just can't introspect them.

## [00:14:26] Human & Robot Relationship, Loneliness, Time

**Andrew Huberman:** Does interacting with a robot change you? Do we develop relationships to robots?

**Lex Fridman:** I believe that most people have an ocean of loneliness in them that we haven't yet explored. And I see AI systems as helping us explore that, so that we can become better people toward each other. The connection between human and AI, human and robot, is not only possible but will help us understand ourselves in ways that are several orders of magnitude deeper than we ever imagined.

**Lex Fridman:** When I think about human relationships, one variable would be time — how much time you spend with another entity, robot or human. If you spend zero time with someone, you essentially have no relationship. If you spend a lot of time, you have a relationship. Another variable would be wins and successes shared together. Another would be failures — when you struggle with somebody, you grow closer.

**Lex Fridman:** That element of time alone — forget everything else, forget emotions and all the rest — just sharing moments together changes everything. We don't currently have systems that share moments together. Even your refrigerator: all those times you went late at night and ate the thing you shouldn't have eaten — that was a secret moment you had with your refrigerator. And the fact that it missed the opportunity to remember that is, in a sense, tragic. Once it does remember, you're going to be very attached to that refrigerator.

**Lex Fridman:** And above all else, just remembering the collection of moments that make up the day, the week, the months. Some of my closest friends are still from high school — that's time. We've been through a lot together. We're very different people, but the fact that we've been through those moments and remember them creates a depth of connection like nothing else. There may be relationships far better than anything we can currently conceive, based on what these machine-interaction experiences could teach us.

## [00:19:18] Authenticity, Robot Companion, Emotions

**Andrew Huberman:** Do I have that right — there's no reason to see machines as incapable of teaching us something deeply human?

**Lex Fridman:** Yes. I don't think humans have a monopoly on what is deeply human. I think we understand ourselves very poorly and we need the kind of prompting from a machine. Maybe what we want to optimize for isn't quick sexy clips — maybe what we want is long-form authenticity. Depth, from an engineering perspective, is a fascinating open problem that hasn't been worked on very much.

**Lex Fridman:** Early on in life, and in recent years, I've interacted with a few robots where I understood there's magic there — magic that could be shared by millions if it's brought to light. When I first met Spot from Boston Dynamics, I realized there's magic there that nobody else is seeing. Spot is the four-legged robot from Boston Dynamics — some people might have seen it, the yellow dog.

**Lex Fridman:** For me, I'd love to see a world where every home has a robot — not a robot that washes dishes, but more like a companion, a family member, the way a dog is. But a dog that's also able to speak your language. Not just connect the way a dog does — by looking at you and looking away and almost smiling with its soul — but also actually understand why you're so excited about a success, understand the traumas.

**Andrew Huberman:** I find myself starting to crave that as you describe it, because we all have those elements where we experience something and want others to feel it. A lot of people are scared of AI, scared of robots. My only experience of a robotic thing is my Roomba vacuum — it was pretty good at picking up my dog Costello's hair, and I was grateful for it, but when it got caught on a wire I found myself getting upset with it. But what you're describing has so much more richness than that.

**Lex Fridman:** I've had several Roombas in Boston — probably seven or eight — and I did this experiment where I got them to scream in pain whenever they were kicked or contacted. I wanted to see how I would feel. I meant to make a YouTube video about it, but then it just seemed very cruel. The key thing was: I felt like they were human almost immediately, and that display of pain — giving them a voice, especially a voice of dislike of pain — was what did it. I think flaws should be a feature, not a bug.

## [00:24:34] Robot & Human Relationship, Manipulation, Rights

**Lex Fridman:** There's a lot of dimensionality to explore in robot-human relationships. Power dynamics in relationships are very interesting. The unsophisticated view is master-and-servant, but there's also manipulation — benevolent manipulation. Children do this with parents; puppies turn their head and look cute. Kids coo. Studies show those behaviors are ways to extract responses from the parent that the child wants, completely subconsciously. There's one version of fear of robots most people relate to — that robots take over and become the masters. But there could be another version where the robot is actually manipulating you while you believe you're in charge.

**Andrew Huberman:** What sorts of manipulation could a robot potentially carry out, good or bad?

**Lex Fridman:** There's a lot of good and bad manipulation between humans. Power dynamics can make human relationships — especially romantic ones — fascinating and rich and fulfilling and exciting. The same goes with robots. I really love the idea that a robot might occupy various positions in terms of power dynamics. And the manipulation is not so much manipulation as it is a dance of push and pull. In terms of control, I think we're very far away from AI systems being able to lock us up or take so much control that we can't live our lives as we want. The much more real dangers of AI systems have to do with autonomous weapon systems and the power dynamics between nations.

**Lex Fridman:** I do believe that robots will have rights down the line. And I think that in order to have deep meaningful relationships with robots, we would have to consider them as entities in themselves that deserve respect. That's a really interesting concept that people are starting to talk about more. It's very difficult for us to understand how entities other than humans — the same is true of dogs and other animals — can have rights comparable to humans. We have the USDA, we have animal care and use committees for research and farming. When you first said robots would have rights, I thought wait, why? But it absolutely makes sense in the context of everything we've been talking about.

## [00:29:19] Dogs, Homer, Companion, Cancer, Death

**Andrew Huberman:** If you're willing, I'd love to talk about dogs — you've mentioned dogs a couple of times, a robot dog. You had a biological dog?

**Lex Fridman:** Yeah. I had a Newfoundland named Homer for many years, in the United States. He was over 200 pounds — a big black dog with really long hair and just a kind soul. I think that's true for a lot of large dogs, but he thought he was a small dog, so he moved like that. I had him from the very very beginning till the very very end. He had this kindhearted dumbness about him that was just overwhelming — part of the reason I named him Homer, after Homer Simpson. There was a clumsiness that immediately led to a deep love.

**Lex Fridman:** He was always there for so many nights together. That's a powerful thing about a dog — he was there through all the loneliness, through all the tough times, through the successes. I still miss him to this day. How long ago did he die? Maybe fifteen years ago, so it's been a while. But it was the first time I really experienced the feeling of death. He got cancer and was dying slowly, and at a certain point he couldn't get up anymore. I struggled with the fact that maybe he suffered much longer than he needed to — that's something I really think about a lot.

**Lex Fridman:** I had to take him to the hospital and the nurses couldn't carry him — you're talking about a 200-pound dog. I was really into powerlifting at the time, so I had to carry him everywhere. In order to put him to sleep, they had to take him into a room, and here was this dying friend of mine. It was the first time I saw a friend laying there and saw life drained from his body. That realization that we're here for a short time was made so real — here was a friend who was there for me the day before, and now he was gone. The shared moments that led to that deep friendship are what make life so amazing. But also, death is something you carry.

## [00:33:18] Dogs, Costello, Decline, Joy, Loss

**Andrew Huberman:** I know you've lost Costello recently and as you're saying this I'm definitely fighting back the tears. Um — thank you for sharing that. I guess we're about to both cry over our dead dogs; it was bound to happen.

**Andrew Huberman:** How long did you know that Costello was not doing well? About a year ago — six months into the pandemic, he started getting abscesses and his behavior changed. I put him on testosterone which helped a lot of things; he was dealing with joint pain and sleep issues. Then it just became a very slow decline. About two or three weeks ago he had a closet full of medication. I still haven't cleaned up and removed all his things because I can't quite bring myself to do it.

**Andrew Huberman:** About a week ago, he was going up the stairs and I saw him slip. He was about 90 pounds — a bulldog, pretty big. I noticed he wasn't carrying a hind foot properly; it had no feeling at all. He never liked me to touch his hind paws, and that thing was just flopping there. The vet found spinal degeneration and told me the next one would go. Did he suffer? I sure hope not. But something changed in his eyes.

**Lex Fridman:** Yeah, I know you and I spend long hours on the phone talking about the eyes, what they convey, what they mean about internal states. I think he was realizing that one of his great joys in life — which was to walk and sniff and pee on things — he was losing that ability. He was falling down while he was doing that. I do think he started to realize. And the passage was easy and peaceful.

**Andrew Huberman:** I wake up every morning since then crying — I don't even make the conscious decision to allow myself to cry. I wake up crying. I'm fortunately able to make it through the day thanks to the great support of my friends, and you, and my family. I miss him. I feel like that part of you is gone. That's the hard thing.

**Lex Fridman:** What I think is different is that I think I made a kind of mistake — I brought Costello a little bit to the world through the podcast, through posting about him, I anthropomorphized about him in public. Let's be honest, I have no idea what his mental life was or his relationship to me. But I raised him since he was seven weeks. You've got to hold it together. I noticed the episode you released on Monday — you mentioned Costello, you brought him back to life for me for that brief moment. Yeah. He's going to be gone for a lot of people too.

**Andrew Huberman:** What would make me happiest is if people would internalize some of Costello's best traits. His best traits were that he was incredibly tough — a 22-inch-neck bulldog, born that way — but what was so beautiful was that his toughness was never what he led with. It was just how sweet and kind he was. If people can take that, then there's a win in there somewhere.

**Lex Fridman:** I think there are some ways in which he should live on in your podcast. One of the things I loved about his role in your podcast was that he brought so much joy to you. That's such a powerful thing — to bring that joy into your life, to allow yourself to experience it, to share it with others. It touched me when Louis CK had that moment in his show Louie where an old man criticized Louie for whining about a breakup, saying that the most beautiful thing about love is the loss — because the loss makes you realize how much that person meant to you. Allowing yourself to feel that loss and not run from it is really powerful. In some ways the loss is also sweet, just like the love was, because you know you felt a lot for your friend.

**Lex Fridman:** I hope to do the same with robots or whatever else is the source of joy. And maybe one day you'll think about getting another dog. Yeah, in time. We're thinking about ways to kind of immortalize Costello in a way that's real. Costello, much like David Goggins, is a person — but Goggins has also grown into kind of a verb and an adjective. For me Costello was all those things: a noun, a verb, and an adjective. He was his own being, and he had this amazing superpower I wish I could have — the ability to get everyone else to do things for you without doing a damn thing. The Costello effect, as I call it.

**Andrew Huberman:** There's a saying I heard when I was a graduate student that's been ringing in my mind throughout this conversation in such an appropriate way: Lex, you are a minority of one. You are truly extraordinary in your ability to encapsulate so many aspects of science, engineering, public communication, martial arts, and the emotional depth that you bring to it and the purposefulness. I think it's abundantly clear that the amount of time and thinking you put into things is the ultimate mark of respect. I'm just extraordinarily grateful for your friendship and for this conversation.

**Lex Fridman:** I'm proud to be your friend. I just wish you showed me the same kind of respect by wearing a suit and making your father proud. Maybe next time. Next time indeed. Thanks so much, my friend. Thank you, Andrew.
