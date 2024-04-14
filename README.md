# Subword-Spotting
NLP course Final Project

by: Daniel Bazar 314708181 & Lior Krengel 315850594

## Goal
1) identify a linguistic or language-related phenomenon or task that an LLM does not perform well on.
2) demonstrate that it indeed does not perform well on this task.
3) analyze and quantify the patterns of failure.

## The task
we demonstrate a type of word puzzle that involves identifying embedded words within other words. Specifically, this puzzle asks to find a subword that is also the name of an object from some category (for example, colors, animals, etc.). while humans perform well on this task, LLM doesnt.  
example question:
<pre>
which one of the following words contains a subword of an animal?
a. guitar
<b>b. million</b> (contains "lion")
c. pasta
d. house
</pre>

# WIP
```diff  
- ## Methodology of evaluation
- For testing LLMs for this task we conducted several experiments with various types of prompts on a dataset we created. 
- Some of the prompting techniques we used are zero-shot, few-shot, chain-of-thought, decomposition, etc. 
- For evaluation we compare the accuracy on different experiment with humans performance.
- ### Technical detailes
- we used models a, b, c with temperature 0 and so on

- ## The Dataset
- format of the dataset, some examples, how we created it and so on........

- ## Results
- Graphs and so on
```
