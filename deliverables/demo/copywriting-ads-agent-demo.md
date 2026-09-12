# Copywriting & Ads Agent Demo

## Objective
Demonstrate that Agent 2 (Copywriting & Ads Agent) creates persuasive, platform-specific marketing copy using dedicated workflows, rather than relying on a single generic prompt. Show how it validates constraints (like Google Ads limits) and handles optional ad creative generation.

## Scenario
We will demo the **Google Ads Workflow** to show how the agent handles strict constraints and search intent, followed briefly by the **Facebook Ads Workflow** to demonstrate image generation (or its graceful fallback).

---

## Part 1: Google Ads (Constraint & Intent Matching)

### Input
- **Product/Service:** Enterprise Cloud Backup Solutions
- **Target Keywords:** enterprise cloud backup, ransomware protection, secure data recovery
- **Search Intent:** High-intent IT directors looking for secure, reliable backups after a recent industry ransomware scare.
- **Target Audience:** IT Directors, CIOs
- **Key Benefits:** 99.999% uptime, immutable backups, 15-minute recovery time
- **Offer/CTA:** Book a Demo

### Steps
1. Select **Google Ads** from the sidebar.
2. Fill in the brief with the details above.
3. Click **Generate Copy**.

### Workflow Explanation
*While it's generating, explain:*
"A generic chatbot would just write a paragraph. This agent follows a specialized workflow: First, it analyzes the search intent to understand *why* the IT Director is searching. Second, it drafts headlines and descriptions. Finally, it runs a validation step to ensure absolutely no headline exceeds Google's strict 30-character limit."

### Generated Copy
*Show the Final Output tab.*
- Point out that all headlines are under 30 characters.
- Point out the specific inclusion of the target keywords and the CTA.
*Switch to the Strategic Analysis tab.*
- Show the intent analysis that the agent performed before writing the copy.

---

## Part 2: Facebook Ads (Persuasion & Image Generation)

### Input
- **Product/Service:** Lumina Ergonomic Office Chair
- **Target Audience:** Remote workers in their 30s
- **Campaign Objective:** Direct sales
- **Key Benefit:** Fixes posture in 7 days
- **Pain Point:** Lower back pain after sitting for 4 hours
- **Brand Tone:** Empathetic, modern, direct
- **Generate Image Creative:** [Checked]

### Workflow & Image Generation Explanation
*While it's generating, explain:*
"This workflow uses a completely different set of instructions focused on scroll-stopping hooks and empathy. It also uses a separate `ImageGenerator` service. The agent writes the copy, extracts a visual prompt from that copy, and then calls the image API. The image generation is decoupled so if the API fails, the text generation still works perfectly."

### Generated Copy & Image
*Show the Final Output tab.*
- Read the first line (the hook) to show how it addresses the pain point directly.
*Show the Ad Creative (Image) tab.*
- If the image generated successfully, show it.
- If it fell back gracefully, explain: "The image API was unavailable, but the agent handled this gracefully by returning a detailed visual recommendation for a human designer."

---

## Speaking Script (1–2 minutes)

> "This is Agent 2 — the Copywriting & Ads Agent. While Agent 1 writes long-form content, Agent 2 is purely focused on persuasion and conversion. It handles six specific marketing channels.
>
> I'll start with Google Ads. Google Ads are extremely strict — headlines can't be over 30 characters. [Fill form and click generate]. 
>
> Behind the scenes, the agent isn't just writing an ad. It analyzes the search intent, drafts the copy, and then reviews its own work to guarantee the character limits are respected. This is what makes it an agentic workflow. [Show output]. As you can see, the headlines are punchy, keyword-rich, and perfectly within limits.
> 
> Let's look at Facebook Ads. For Facebook, we need to interrupt the scroll and address pain points. I've checked the 'Generate Image Creative' box. [Click generate].
> 
> The agent first writes the copy using a persuasive framework. Then, it extracts a visual recommendation and passes it to a completely separate Image Generation service. By keeping the text and image generation decoupled, the application remains robust. [Show output]. Here is the generated copy with a strong hook, and here in the next tab is the accompanying ad creative."
