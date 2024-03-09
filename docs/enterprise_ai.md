 <img src="./images/enterprise_ai_1600x840.png" alt="AI Navigating the Enterprise"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">

# Exploring Enterprise AI
*Integrating Systems with Generative AI*
 

I'm participating in a [TM Forum](https://www.tmforum.org) [Catalyst Project](https://www.tmforum.org/catalysts) called [AI-driven end-to-end offer lifecycle management](https://www.tmforum.org/catalysts/projects/C24.0.654/aidriven-endtoend-offer-lifecycle-management), which has several objectives, one of which has me thinking about the different roles of Generative AI within large enterprise systems and how it can best be leveraged.

In particular, can [Tool Augmented Generative AI](https://mechanician.ai/daring-mechanician), which is equipped with tools that enable it to interact with different enterprise systems, play the role of a systems integration layer?


#### Enterprise Chatbots

The most obvious and very useful role for an Enterprise Generative AI is as a RAG-enhanced chatbot that answers questions using enterprise data for both internal users and customers.


>***But Generative AI can do more than just answer questions***


### AI-Based Systems Integration

*Can Generative AI be used to bridge different systems, orchestrate complex tasks, and provide insights that are not readily available from other tools?* Given its ability to interpret, translate, and correlate data from various systems, Generative AI could serve as a general-purpose system integration layer for enterprise systems. 

*How will the integration of Generative AI into enterprise systems change their design and usage?*

*How will existing enterprise APIs evolve to support this integration?*


> **Note: RAG and TAG**

>You can feed data from different systems into a Generative AI model and use that model to answer questions about it. This method is known as the **Retrieval Augmented Generation** (RAG) approach. While RAG is an effective approach, making data from various enterprise systems available in an external datastore, indexed with the necessary embeddings for the RAG approach, is not always feasible. If Generative AI is given tools to access data directly from those systems, it can pull the data it needs, as opposed to being pushed data that may not be necessary. This method is referred to as *Tool Augmented Generation* (TAG).

>**Note: TAG vs Agents**

>What I refer to as **Tool Augmented Generation** (TAG) is commonly known as **Agents** or the **Agentic** approach. *Agents* have existed in various forms for a long time, carrying years of context regarding their meanings and capabilities. Therefore, to distinguish Generative AIs equipped with tools, I prefer using the term *TAG*.


### Enterprise Systems
 
Enterprises contain a large number of specialized systems, each managing a subset of the enterprise's data and performing a subset of the specialized tasks that drive an enterprise.

* **CRM** Systems
* **ERP** Systems
* **Billing** Systems
* **Reporting** Systems
* **Product Inventory** Systems
* **Product Catalogs** Systems
* **Configure, Price, Quote** (CPQ) Systems
* **Field Operations** Systems
* **Contract** Systems
* **Commision** Systems
* **Machine Learning** Systems
* ...


>*What value can an AI-based approach to integrating these systems provide that traditional systems integration approaches can't?*


### Loose Coupling Through AI

Generative AI excels at **summarizing** data, **correlating** data, **answering questions** about data, and even **building narratives** to explain data.

This proficiency enables it to navigate among, translate between, and smooth over different APIs and data formats.

Acting as an intermediary, Generative AI loosely couples the systems it interacts with, interpreting and correlating data from different systems as necessary.


### Translating Intent into Action

When equipped with tools that enable interaction with different enterprise systems, Generative AI is surprisingly adept at inferring a user's intent during interactions. It can translate this intent into one or more actions, performing multi-step tasks across various systems. By applying its tools to retrieve, create, and update data, it simplifies complex tasks for users.


### Navigating Complex Systems

Generative AI can **drive interactions** and **guide users** through multi-step processes by prompting them for more information at each step.

By engaging with users to answer questions that require information spanning multiple systems, Generative AI can assist users in uncovering relationships in the data that they might not have identified independently.

Generative AI serves as a dynamic, exploratory, interactive tool for navigating various systems, driven by a user's interaction and intent.



## Case Study: AI-Driven End-to-End Offer Lifecycle Management

There are numerous ways that Generative AI can be used to integrate different enterprise systems. However, let's focus on one of the objectives of the [AI-driven end-to-end offer lifecycle management project](https://www.tmforum.org/catalysts/projects/C24.0.654/aidriven-endtoend-offer-lifecycle-management). This objective is to leverage *Generative AI* in assisting with the creation of "**good**" offers.


### What is an Offer?
 
So the first question to answer is, *what is an offer?*
 
I'll let *ChatGPT* explain...
 
>*An offer in the context of a communication services company typically refers to a package or deal that the company presents to its customers or potential customers. These offers are designed to promote the company's communication services, which can include telephone services, internet access, cable television, mobile communications, and more. Here are some key components and characteristics of such offers:*

>1. **Service Bundles**: *Offers may include various combinations of services at a discounted rate. For example, a company might bundle internet and cable TV services together at a lower price than if a customer were to purchase each service separately.*

>2. **Promotional Discounts**: *These are special pricing strategies used to attract new customers or retain existing ones. This could involve reduced prices for a limited time, waived installation fees, or free upgrades to higher service tiers for a certain period.*

>3. **Limited-Time Deals**: *Offers are often time-sensitive, encouraging customers to act quickly to take advantage of the best rates or additional perks.*

>4. **Customizable Packages**: *Some offers allow customers to customize their service package according to their needs, choosing from a variety of channels, internet speeds, or data plans.*

>5. **Loyalty Rewards**: *Offers might include benefits for long-term customers, such as discounts, exclusive access to new products or services, and other loyalty rewards.*

>6. **Introductory Offers**: *These are designed for new customers and may provide significantly reduced rates for the first few months of service, after which standard rates apply.*

>7. **Contract Terms**: *Many offers come with specific contract terms, including the length of the contract, early termination fees, and conditions under which the offer remains valid.*

>8. **Value-Added Services**: *Offers might also include additional services at no extra cost, such as access to premium channels, cloud storage, or cybersecurity packages.*

>*In essence, offers from communication services companies are marketing strategies intended to attract and retain customers by providing them with compelling value propositions. These offers are carefully crafted to balance customer appeal with business objectives, aiming to increase subscriber numbers, boost customer satisfaction, and drive long-term revenue growth.*
 

### Identifying and Generating Good Offers
 
With this basic knowledge of what an offer is, the objective leads to three more questions.
 
* **How do we identify good offers?**
* **Can we automate the creation of *good* offers?**
* **What is the role of Generative AI in identifying and creating *good* offers?**


We can connect an **EVALUATION** process, which *identifies* good offers, with a **GENERATION** process, which *creates* the offers, through an intermediate **REPORTING** step. This step synthesizes the evaluation results into a narrative. Such a narrative guides the *generation process* and also informs product marketing managers about how different offer characteristics impact performance.


### EVALUATION: 

Start by using traditional data analysis approaches, ML models, and the built-in capabilities of each enterprise system to evaluate the performance of existing offers based on a variety of KPIs, such as conversion rate, ROI, and resource utilization.


#### How do we identify a good offer?

The answers to this question can vary widely, but the following *KPIs* can be used to measure the quality of a product offer.


#### Key Performance Indicators (KPIs) for Offers

* **High Conversion Rate** (desirability of offer): the percentage of users who take an offer out of the total number of visitors that received the offer.

* **Return on Investment or Profitability**: a function of costs, pricing, and sales volume.

* **Resource Optimization**: uses inventory (network resources and equipment) that is readily available, not resource constrained or limited or expensive

* **Offer Simplicity**
    * the offer is simple to understand for customers
    * the offer is simple to understand for product marketing managers
    * offer is not redundant to other offers
    * offer is built from a simple set of components

* **Marketability**: *Can this offer be effectively marketed?*



>**When Not to Use Generative AI**

>Generative AI might not excel in tasks that involve using data to *predict*, *forecast*, *detect complex patterns*, and *calculate*; for these activities, other tools and systems are more suitable.

>Although Generative AI is effective at summarizing data, it may not perform well with large, complex data sets where traditional statistical analysis or machine learning could offer better summarization.

>However, once the data has been summarized, Generative AI can play a role in explaining the results. It builds narratives that make the findings accessible to business stakeholders who need to understand them. With the right tools, Generative AI can also correlate these results with data from other systems, often providing insightful and unexpected perspectives.


#### Generating KPIs for Offers from Enterprise Systems

The data needed to evaluate these KPIs comes from various systems across an enterprise, as do the approaches for evaluating the KPIs, including, in some cases, the use of Generative AI.


* **Conversion Rate**: Given records of past offers, and their conversion rates, *can we predict what attributes contribute to high conversion rates, and then generate offers that are likely to have high conversion rates?*
  * *Example Data Sources*: **CRM**, **Product Catalog**, **CPQ** systems, **Reporting** Systems
  * *Example Predictions*: *What offer characteristics have the most affect on the conversion rate?*
  * *How are conversion rates affected by changes in different offer characteristics?*
    * *Service Bundles*, *Promotional Discounts*, *Limited-Time Deals*, *Customizable Packages*, *Loyalty Rewards*, *Introductory Offers*, *Contract Terms*, *Value-Added Services*
  * *Evaluator*: Machine Learning systems, specialized conversion rate analysis systems.

* **ROI**: Given data on cost analysis, pricing strategies, and sales volumes of previous offers, can we simulate different pricing strategies and cost structures, estimating the ROI of new offers based on projected sales volumes, and then generate offers that are profitable?
  * *Example Data Sources*: **ERP**, **Billing** Systems, **Reporting** Systems.
  * *Example Predictions*:
      * a combination of equipment, network resources, customer segment, region that will optimize delta between cost and pricing while maintaining an appropriate sales volume.
  * *Evaluator*: Machine Learning systems, specialized cost analysis systems.

* **Supply Chain Optimization**: Can we review resource inventory and utilization reports and generate offers that are feasible and sustainable without overextending or underutilizing assets.
  * *Example Data Sources*: **ERP**, **Billing** Systems, **Reporting** Systems.
  * *Example Predictions*:
     * *Does this offer provide a combination of equipment and network resources at a cost that will enable a desirable level of profitability with pricing that will lead to acceptable conversion rate (desirability)?*
     * *Does this offer use equipment and resources that are readily available, not supply constrained, limited, or expensive?*
  * *Evaluator*: Machine Learning systems, specialized supply chain optimization systems.

* **Offer Simplification**: *Can we evaluate the simplicity of an offer?*
  * *Example Data Sources*: **Product Catalog** Systems
  * *Evaluate*:
    * *Is the value of this offer going to be apparent to customers?*
    * *Is the value of this offer apparent to the product marketing manager?*
    * *Are there existing offers that are too similar to the generated offer?*
    * *Is the offer built with unnecessary components, adding unnecessary complexity?*
  * *Evaluator*: Generative AI, Product Marketing Managers
  * This evaluation can be performed by a Generative AI that assesses each offer based on the questions above. This process can also be interactive, driven by the product marketing manager's questions.  

* **Marketability**: Can we analyze marketing data, predicting the market penetration potential of new offers and identifying optimal marketing strategies, and generate offers that are effectively marketed?
  * *Can we generate compelling marketing material for the offer?*
  * *Can it be effectively marketed?*
  * *Is the value of this offer apparent to the potential customer?*
  * *Is the value of this offer apparent to the product marketing team?*
  * *Evaluator*: Generative AI
  * This evaluation can be performed by a Generative AI that assesses each offer based on the questions above. This process can also be interactive, driven by the product marketing manager's questions.


### REPORTING

* Use Generative AI to gather and synthesize results from each evaluation system, constructing a narrative for product marketing managers. This narrative will detail how various characteristics of existing offers impact different KPIs, considering factors like product category, targeted customer group, and region.

* This interactive reporting process, driven by the product marketing manager's inquiries, leverages the assessments to inform the creation of new offers. 

This reporting process is an example of using Generative AI to integrate different enterprise systems, and synthesize results from these systems.


### GENERATION

* Using the insights from the generated report, the Generative AI is directed to proppose new offers for specific product groups within a given business unit and region.

* These proposals are based on building blocks—components and features of offers—predicted to excel according to the evaluated KPIs. Such building blocks include service bundles, promotional discounts, limited-time deals, customizable packages, loyalty rewards, introductory offers, contract terms, and value-added services.

* The offer generation process is designed to be interactive, allowing product marketing managers to guide the development of these offers actively. 

* Once an offer receives approval from the product marketing manager, the Generative AI is tasked with integrating the offer into the enterprise Product Catalog System.

This generation step is an example of Generative AI navigating and leveraging various enterprise systems to undertake complex, multi-step tasks—such as retrieving, creating, and updating data across these systems.



<!-- An example of this last step can be found in the [Daring Mechanician Product Catalog Example](https://github.com/liebke/mechanician/tree/main/examples/product_catalog). -->
