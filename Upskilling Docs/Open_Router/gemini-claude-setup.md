# Gemini and Claude

As part of my role in model selection for our project, I have explored
the availability of free API keys for advanced large language models
such as Claude and Gemini. Since our project extends over a three-year
period, there is a high likelihood that we will require access to
commercial models in the future. To ensure continuity without incurring
additional costs, I researched ways to obtain free access under
educational or trial provisions. Both Claude and Gemini provide options
for students, researchers, and developers to experiment with their APIs
at no charge, though these come with specific usage limits and
conditions. Understanding these restrictions early allows us to plan
effectively and avoid unexpected disruptions. I have also documented the
process of applying for these keys, outlining the requirements for
eligibility, the terms of use, and the limitations on request quotas.

In addition, I have prepared simple sample code demonstrating how to
integrate these APIs into a project environment. This serves as a
reference for future trimesters, enabling team members to quickly adopt
and test these models without starting from scratch. This proactive
preparation ensures that our project remains sustainable,
cost-effective, and ready to leverage the latest commercial AI tools.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image1.png"
style="width:6.5in;height:3.5625in" />

- On this screen, click **Get API key**.

- The “Try Gemini” button is only for testing prompts inside Google AI
  Studio, which is fine if you just want to play around.

- But for project work, you need the API key so you can connect Gemini
  directly to your code (like Python or Node.js).

- Once you click this, you’ll be taken to Google AI Studio where you can
  generate your key.

This key is what you’ll use later to access Gemini programmatically in
your project.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image2.png"
style="width:6.5in;height:3.0625in" />

- Once you click “Get API key,” you’ll be taken to the Google AI Studio
  API Keys page.

- Here, you can create and manage your keys as well as see example code
  for testing Gemini.

- To generate your first key, click on the “+ Create API key” button,
  and a unique key will appear under your project details.

- This key is what you’ll use later in your code to connect with Gemini.

- Make sure to copy it and store it safely, because you’ll need it every
  time you run your project.

- It’s also important not to share your key publicly or upload it to
  GitHub. Instead, save it securely in a .env file or similar.

- Once the key is ready, you can even use the sample code provided on
  this page to test that Gemini is working correctly.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image3.png"
style="width:5.15625in;height:2.41667in" />

- At this stage, the system asks you to select a Google Cloud project
  where the API key will be created.

- By default, a project called “Gemini API” is already available, so you
  don’t need to set up a new one. Simply select this project and then
  click on “Create API key in existing project.”

- This will generate your API key inside the chosen project.

- Once created, the key will appear on your API Keys page, and you can
  copy it to use in your code.

- This step links the key to your Google Cloud project so it can be
  managed securely and tracked under your account.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image4.png"
style="width:5.20833in;height:2.45833in" />

- Here, the Google Cloud project named “Gemini API” is displayed and
  ready to be selected.

- Simply click on this project to highlight it and then proceed with
  “Create API key in existing project.”

- This step confirms that the key will be generated under the Gemini API
  project, which is already set up for you.

- Once confirmed, the system will create a new API key that you can copy
  and use in your code.

- This ensures that your key is tied to a valid project, making it
  easier to manage and track inside Google Cloud.

![](./Media/Claude_and_gemini_pics_run2/media/image5.png)<img
src="./Media/Claude_and_gemini_pics_run2/media/image6.png"
style="width:6.48958in;height:1.86458in" />

- Once the project is selected, the system generates your API key.

- This key is the unique identifier that allows your code to connect
  with Gemini.

- At this stage, you should click Copy and save the key in a safe place,
  such as a .env file, so it stays hidden from others.

- Never share this key publicly or paste it directly into code that
  could be uploaded to GitHub or any public platform, because anyone
  with access to it could use up your quota.

- From this point on, the API key is what you’ll use in your project
  whenever you want to make requests to Gemini.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image7.png"
style="width:6.48958in;height:3.69792in" />

- After generating the key, it will now appear on the API Keys page
  under your project details.

- Here you can see the project number, project name, your API key, the
  date it was created, and usage options.

- At the top of the page, there is also a code snippet showing how to
  quickly test Gemini using a curl command.

- You can use this snippet to confirm that your key is working by making
  a sample request to Gemini.

- From this point, your API key is ready to be used in any programming
  environment such as Python or Node.js. Just remember to store it
  securely (like in a .env file) and never paste it directly into code
  that could be made public.

- This page is also where you can manage multiple keys in the future if
  you need them.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image8.png"
style="width:4.41667in;height:1.78125in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

- At this point, a message may appear saying “This project has no
  billing account.” This simply means that the Google Cloud project is
  not linked to any payment method.

- For students, this usually isn’t an issue because free trial credits
  or limited free usage are often enough to test and run small projects.

- If billing is ever required, you can link a billing account from this
  page, but for learning and experimentation purposes, you can continue
  using the free tier without setting up payments.

- It’s a good reminder to always check your usage and stay within free
  limits to avoid any unexpected charges.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image9.png"
style="width:6.5in;height:1.78194in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

- This screen shows the Billing Account Management page.

- Here, no billing accounts are currently linked, which is why the table
  is empty.

- For most student projects, a billing account is not necessary because
  Google provides limited free usage and trial credits to experiment
  with the API.

- If you ever need to enable full access or go beyond the free tier,
  this is where you can create and link a billing account.

- Until then, you can simply skip this step and continue using the free
  resources provided, making sure to stay within the usage limits.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image10.png"
style="width:4.91667in;height:3.61458in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

- This screen is where you set up your billing profile. It shows your
  contact information and gives the option to add a payment method.

- For student or free-tier use, this step is usually optional unless you
  plan to go beyond the free credits.

- If you want to continue with free usage only, you don’t need to add a
  payment method.

- However, if full access is required in the future, this is where you
  would link a card or payment method and then click Submit.

- For now, as a student project, you can safely skip adding billing and
  continue using Gemini under the free plan limits.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image11.png"
style="width:4.72917in;height:3.89583in"
alt="A screenshot of a credit card AI-generated content may be incorrect." />

- This step asks you to add a credit or debit card, and providing these
  details is necessary for account verification.

- Even if you are only planning to use the free tier, Google Cloud
  requires a valid card to confirm your identity and prevent misuse of
  the service.

You will need to enter your card number, expiry date, security code, and
cardholder name, then click Save card.

- While the card is required for verification, you won’t be charged as
  long as you stay within the free tier limits or use the free credits
  provided.

- This step is important because without verifying your account with a
  card, you won’t be able to activate and use the Gemini API key.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image12.png"
style="width:6.5in;height:3.47292in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

- Once the card details are added and your account is verified, you’ll
  see the Google Cloud Billing Dashboard.

- This page shows an overview of your account costs, usage, and budgets.

- Since the account is new, the cost will be \$0.00, and you won’t see
  any charges unless you exceed the free tier or use services outside of
  the free credits.

- From here, you can also set up a budget alert to get notified if your
  spending reaches a certain amount, which is useful for staying safe
  from unexpected costs.

- The dashboard also displays your top projects and services, so you can
  keep track of what is using resources.

- For student projects, it’s important to check this page regularly to
  ensure you are staying within the free usage limits and not generating
  unnecessary charges.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image13.png"
style="width:6.5in;height:6.15903in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

- For Claude, the setup process starts with email verification.

- Here, you need to enter the verification code that was sent to your
  registered email address (in this case, your Deakin student email).

- Simply check your inbox, copy the code, and paste it into the “Enter
  verification code” field. Then click on “Verify Email Address.”

- This step confirms your identity and activates your Claude account.

- Without completing this verification, you won’t be able to access
  Claude’s features or generate an API key, so it’s an essential step
  before moving forward.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image14.png"
style="width:6.5in;height:4.18125in"
alt="A screenshot of a computer screen AI-generated content may be incorrect." />

Here, Claude shows the different **plans** available. For students and
small projects, the **Free plan** is the best option to start with
because it costs nothing (AUD 0) and still allows you to -

- Chat with Claude on web, iOS, and Android

- Write, edit, and create content

- Analyze text and upload images

- Generate code and visualize data

- Use web search inside the chat

If you later need more features or higher usage limits, you can upgrade
to the Pro plan (AUD 26/month) or the Max plan (AUD 154.54/month). But
for testing and academic use, simply click “Use Claude for free” to
continue. This lets you start experimenting right away without any
payment.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image15.png"
style="width:6.5in;height:2.14653in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

- Now that the account setup is complete, the Claude dashboard gives
  different options to start building. You can either create a prompt,
  generate a prompt, or most importantly, get an API key.

- For project work and integration with code, the option to focus on is
  “Get API Key.” Clicking this will generate a key that you can use in
  your applications, like what was done earlier with Gemini.

- The key allows you to call Claude programmatically and include it in
  your workflows. While Claude may also offer credits or paid options
  for extended use, students can usually begin testing on the free plan,
  making the API key the essential step to connect Claude with your
  project.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image16.png"
style="width:6.5in;height:3.06528in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

- On the screen you can see Claude workspace, where prompts can be
  created and tested.

- At the top, you can see the model version (in this case,
  claude-3.5-haiku-20241022) and options to add examples.

- The System Prompt is where you set the role or instructions for Claude
  here it says, *“You are an educator.*

- *Provide feedback based on the rubric below.”* Underneath, the User
  section is where you type or generate the actual input you want Claude
  to respond to.

For students building projects, this workspace is very useful for
experimenting with different prompts before moving them into code. Once
satisfied, the same prompts can be used with the API key to automate the
process in your project. This makes the Claude workspace both a testing
ground and a reference point for developing structured prompts.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image17.png"
style="width:6.5in;height:3.16736in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

This screen shows the Python code example for connecting to Claude using
the Anthropic API. Here’s how it works -

1.  First, the anthropic library is imported.

2.  The client is created with your API key (replace "my_api_key" with
    the actual key you generated).

3.  A message is then sent to the Claude model
    (claude-3.5-haiku-20241022) with some parameters:

    - max_tokens sets the output length limit.

    - temperature controls randomness (1 = more creative, lower values =
      more focused).

    - system defines the role or context (in this case, an educator
      giving feedback).

    - messages are where you provide the actual user input.

4.  Finally, print(message.content) displays Claude’s response.

This example shows how to quickly test Claude from Python. By copying
this template and adding your own prompts inside the messages list, you
can start integrating Claude into your projects right away.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image18.png"
style="width:6.45833in;height:8.08333in"
alt="A screenshot of a credit card AI-generated content may be incorrect." />

- Since Claude API requires at least a \$5 credit purchase to get
  started, it does not fully align with the goal of only using free
  resources for the project.

- Because of this, the next step is to look for other providers that
  offer free models or free API credits.

- Options like Google Gemini, OpenAI (with limited free credits for new
  accounts), or Hugging Face Inference API often provide free tiers or
  student-friendly access.

- These alternatives can be used without upfront payment, making them
  more suitable for academic projects where the priority is to
  experiment, test, and integrate models without extra costs.

- By exploring these free models, it’s still possible to continue
  building and demonstrating the project effectively while staying
  within the no-cost requirement.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image19.png"
style="width:6.5in;height:3.07639in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

- A great alternative to paying for Claude directly is using OpenRouter,
  which acts as a unified interface for multiple LLMs.

- OpenRouter allows you to access different providers like Google’s
  Gemini 2.5 Pro, OpenAI’s GPT-5 Chat, and Anthropic’s Claude Sonnet 4,
  all from a single platform.

- The main benefit here is that OpenRouter often provides free tiers,
  trial tokens, or promotional credits, depending on the model and
  provider.

- This makes it very useful for students and projects that are focused
  on cost-free exploration.

- Instead of setting up individual billing with each provider, you can
  register on OpenRouter, select a model, and start sending requests
  through their API.

- This approach gives flexibility to switch between models without extra
  setup, while also taking advantage of any free tokens available.

- For academic projects, this is one of the easiest ways to try out
  premium models without paying upfront.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image20.png"
style="width:6.5in;height:4.6in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

Here you can see Claude 3 Haiku listed on OpenRouter. This page provides
all the key details about the model, including its context size, token
limits, and pricing. The important part for students is that OpenRouter
routes requests automatically to the best available provider, which
helps maximize uptime and ensures your request is processed smoothly.

Each provider (like Anthropic or Google Vertex) shows technical details
such as:

- Context size (how much input text it can handle)

- Max output (length of responses)

- Latency (speed of response)

- Throughput (requests handled per second)

- Pricing (if usage goes beyond free or trial limits)

For projects looking to stay within the free tier, OpenRouter sometimes
provides free credits or access through specific providers, making it a
good option for trying Claude models without paying upfront. From this
page, you can also access the API section, where you’ll find the code
snippets and integration details needed to start using Claude through
OpenRouter.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image21.png"
style="width:6.5in;height:4.51806in"
alt="A screenshot of a chat AI-generated content may be incorrect." />

- Here, the next step is to create an API key in OpenRouter.

- By clicking the “Create API key” button, you’ll generate a unique key
  that lets you access Claude 3 Haiku (and other models)
  programmatically through the OpenRouter API.

- The benefit of OpenRouter is that it uses an OpenAI-compatible API
  format, which means you can use the same kind of request structure as
  with OpenAI’s models. This makes it easier for students to experiment
  since many tutorials and sample codes already follow that format.
  OpenRouter also provides ready-to-use code snippets in Python,
  Typescript, and curl, which you can copy directly and test with your
  API key.

Once the key is generated, remember to store it securely (for example,
in a .env file) and avoid sharing it publicly. From here, you’ll be able
to make requests to Claude 3 Haiku (and other models supported by
OpenRouter) without needing to set up billing directly with Anthropic.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image22.png"
style="width:6.5in;height:2.62292in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

To access Claude and other models through OpenRouter, the next step is
to create an API key. Click on the “Create API Key” button, and
OpenRouter will generate a unique key for your account. This key gives
you access to all supported models, including Claude, Gemini, and
GPT-based ones, without needing separate billing setups for each
provider. Once the key is created, copy it and store it securely (for
example, in a .env file). Never share it publicly or paste it directly
into code that might be uploaded online. With this key, you can now
start making API calls to different models directly from your project.

<img
src="./Media/Claude_and_gemini_pics_run2/media/image23.png"
style="width:4.9375in;height:3.70833in"
alt="A screenshot of a computer AI-generated content may be incorrect." />

Here, you can name your new API key to keep it organized. For example,
the key has been named “aaie” to match the project. You can also set a
credit limit if you want to control how much usage this key allows,
which is useful for preventing accidental overuse — leaving it blank
means unlimited use within your account’s balance. After filling this
out, click “Create” and your new API key will be generated. Once
created, copy it immediately and store it securely in a .env file or
password manager, since it will be required for connecting your project
to OpenRouter’s models.
