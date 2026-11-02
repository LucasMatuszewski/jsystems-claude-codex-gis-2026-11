# Example prompt (dictated) to modernize legacy code

> Repo legacy: https://github.com/sai-pullabhotla/jftp/tree/master#

You are in a very old Java project, in very old versions, which are no longer supported and which will not work here locally on this computer.

I want you to help me modernize this code and create a detailed plan for how we can do it step by step, so that this project works with modern versions of Java and with newer versions of libraries, and above all, so that the app runs and we can use it again (without changing or adding functionalities).

As part of this plan, it suggests that you take the following steps.
1. First of all, at the beginning analyze all the code and make detailed documentation for how this code looks at this moment. Describe all dependencies, describe versions, describe how it works, describe the architecture, make detailed documentation in multiple files. Also create AGENTS.md and CLAUDE.md (importing @AGENTS.md) files that will describe specifically for the agents how they can work in this project, what is here, and what the structure of this project is.
It is very important that you emphasize in the AGENTS.md instructions for the agents that these files must be updated during the execution of the plan and during the modernization of the application, so that AGENTS.md instructions are continuously aligned with how this project actually looks after changes. Documentation of detailed parts of the application and how it all works should be saved in multiple files in Markdown in the /docs folder. However, documentation for the agents in AGENTS.md / CLAUDE.md files should be split into multiple specialized files in the individual parts of the system in nested folders for each specific part of the application. Make one general AGENTS.md file at the main level of the project, whereas the detailed descriptions and instructions for the agents in the individual parts of the project, make it already inside deeper folders, concerning only specific code fragments data.

2. First, do detailed tests regarding the example four functionalities of this application; these can be unit tests that will check whether this application continues to work after our refactor. In these tests, focus on functionality, not on implementation first of all. That is, at the moment when we do the refactor, regardless of the implementation change, the test should still pass if the functionality works. 

3. Try to run this application with minimal changes. Introduce such changes that will be minimally needed for this application to start at the beginning. 

4. After the minimum startup and after the minimum changes needed to run this application, of course check whether the tests still pass. If they do not pass, you must fix something in the application and check whether this functionality was actually broken. Focus on fixing the code, not on fixing the tests. Assume initially that your modified code is wrong, not the tests.

5. At the moment when the application is being launched, and we have tests passing, in such a minimal version, after a minimal refactor of this application, you should make granular commits and move on to the proper larger refactor, updating the versions of various dependencies and also updating the code itself to newer Java standards, so that it is implemented in accordance with the latest guidelines related to Java and modern standards.

---

**END OF PROMPT**

---

## Prompting SMALL Language Models

For small models like Gemma 4 31B, I suggest to split above prompt in multiple smaller prompts.
Small model  has limited context window and attention and big task could be too complicated.

You should also add skills with knowledge for small models, e.g. how to use Mermaid or jUnit 5.

Below are example separate prompts with additional skill names for smaller models:

---

## Example prompt to get architecture analysis

You are in a legacy application in Java that is 14 years old. This application doesn't work currently, so you need to fix some basic issues to run this application for the first time and to install the dependencies. But before you do this, I want you to analyze the code, analyze all the dependencies, and confirm the versions of Java and other libraries we use here. I want you to analyze the design patterns and architecture of this application. This is an FTP client in Java. So you should focus now on understanding and analyzing this application to describe how it works and to make sure that you understand how it works and how to run this application.

You should go deeper inside the folders and analyze the structure of the folders with a depth of 4. You should choose the files that seem to be the most important in this application, based on the structure and the tree that you will generate. You should also analyze the files to better understand the code standards, the version of Java, the design patterns, the design system, and the architecture of this application. So you will understand fully how it works, also based on the most important files. You should read at least 10 files before you will decide to generate the summary.

Also create AGENTS.md and CLAUDE.md (CLAUDE.md should only contain: `@AGENTS.md`) files that will describe specifically for the agents how they can work in this project, what is here, and what the structure of this project is. It is very important that you emphasize in the AGENTS.md instructions for the agents that these files must be updated during the execution of the plan and during the modernization of the application, so that AGENTS.md instructions are continuously aligned with how this project actually looks after changes. Documentation of detailed parts of the application and how it all works should be saved in multiple files in Markdown in the /docs folder. However, documentation for the agents in AGENTS.md / CLAUDE.md files should be split into multiple specialized files in the individual parts of the system in nested folders for each specific part of the application.

Make one general AGENTS.md file at the main level of the project, whereas the detailed descriptions and instructions for the agents in the individual parts of the project, make it already inside deeper folders, concerning only specific code fragments data.

### Example prompt to get Mermaid diagrams with architecture

/design-doc-mermaid
use this skill to analyse data flows and user flows and add mermaid charts. follow instructions from the skill

### Example prompt to get unit tests

/java-junit
I want you to analyze this application, which does not have any tests currently. It's a legacy old application, 14 years old, written in old Java. So you need to make sure that JUnit 5 will work here. Use our documentation to analyze the structure of the application, and based on the documentation choose the five most crucial most important components or parts of code for this application, or classes. And write unit tests for the five elements of this application that you think are most important for the functioning of this application.
