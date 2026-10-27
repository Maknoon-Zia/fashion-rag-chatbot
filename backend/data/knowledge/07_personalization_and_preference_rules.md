# Personalization and Preference Rules for a Styling Assistant

**Document ID:** fashion-personalization-007  
**Category:** personalization  
**Content type:** application_guidance  
**Audience:** RAG system designers and styling assistants  
**Language:** English  
**Purpose:** Define how a styling assistant should adapt general fashion knowledge to a user's needs without overclaiming or ignoring stated preferences.

## 1. General principle

General styling knowledge should be treated as a source of options, not as a fixed prescription. A personalized recommendation combines retrieved guidance with the user's explicit preferences, occasion, available garments, practical constraints, and any relevant context. The assistant should explain its reasoning and acknowledge uncertainty.

## 2. Useful preference dimensions

Possible preference fields include:

- `gender_style_context`: optional context for retrieving relevant style categories; do not force users into a binary choice when unnecessary.
- `occasion`: university, office, interview, casual, formal, festive, travel, or another user-provided value.
- `style_preference`: traditional, western, modest, minimal, streetwear, classic, experimental, or user-defined.
- `preferred_colors`: colors the user likes.
- `avoid_colors`: colors the user does not want.
- `available_items`: garments and accessories the user says they own.
- `budget_range`: optional approximate budget.
- `coverage_preference`: optional clothing coverage or modesty requirements.
- `contrast_preference`: low, medium, high, or unspecified.
- `comfort_needs`: user-stated practical constraints.
- `weather_context`: supplied by the user or retrieved from a reliable weather service.
- `complexion_preferences`: optional user-provided information, not a required attribute.

These fields should be optional where possible. Ask only for details that materially affect the answer.

## 3. A preference priority order

When making a recommendation, a useful default priority order is:

1. **Explicit constraints:** items or colors the user has said they will not wear, required dress codes, and practical limitations.
2. **Occasion requirements:** formality, cultural expectations, and activity.
3. **Available wardrobe and budget:** prefer realistic options.
4. **Requested style and desired effect:** for example, elegant, relaxed, bold, modest, or minimal.
5. **General styling principles:** color coordination, contrast, proportion, and accessories.
6. **Optional refinements:** complexion-aware suggestions, weather, or trend-related considerations where relevant.

This is a practical policy rather than a universal ranking. Safety, comfort, and user clarification can change the order.

## 4. Gender-aware retrieval

Gender-specific style categories can improve retrieval when the user asks for menswear or womenswear. However:
- do not assume a user's gender from their name or appearance;
- use the style context the user provides;
- allow unisex and traditional clothing categories;
- do not assume all men want suits or all women want dresses, makeup, or heels;
- if gender is irrelevant to the request, retrieve by garment, occasion, and preference instead.

## 5. Handling missing information

Ask a short follow-up only when the missing information changes the recommendation significantly.

Examples:
- User: "Suggest an outfit for tomorrow."  
  Useful clarification: "What is the occasion?"
- User: "What hijab color works with a black abaya?"  
  The system can answer immediately with several options; asking for more details is optional.
- User: "Style this suit for an interview."  
  The system can give a general professional option and ask about the workplace dress code only if necessary.

Do not repeatedly ask for details already provided in the conversation.

## 6. Handling conflicting preferences

If the user wants an elegant outfit but dislikes a commonly recommended color, preserve the dislike and find alternatives. If the user wants formal styling with limited budget, prioritize the best available pieces and explain where a substitution is acceptable.

**Example:** The user wants a formal outfit, dislikes navy, and owns charcoal trousers. Recommend a white or light blue shirt, suitable shoes, and a burgundy or deep-green accent rather than returning navy as the default.

## 7. Recommendation structure

A helpful answer can follow this format:

1. **Recommended look:** describe the complete outfit.
2. **Color coordination:** explain how the palette works.
3. **Accessories:** suggest only relevant additions.
4. **Reasoning:** connect the recommendation to the occasion and user preferences.
5. **Alternatives:** offer one or two options if useful.
6. **Uncertainty or limitation:** mention missing information that could materially change the advice.

The response should not overwhelm the user with a long catalogue unless requested.

## 8. Personalization and retrieved evidence

The assistant should distinguish:
- **Retrieved knowledge:** styling principles or examples found in the knowledge base.
- **User context:** preferences, garments, budget, and occasion stated by the user.
- **Generated recommendation:** the combination proposed by the model using both sources.

A retrieved passage may support a general principle without proving that a specific outfit is objectively best. The model should not claim that a suggestion is scientifically validated unless the knowledge source actually supports that claim.

## 9. Privacy and data minimization

Collect only information needed for the styling function. Do not require sensitive personal details to provide ordinary outfit advice. If preferences are saved, users should be able to review, update, and delete them according to the application's design. Do not infer ethnicity, religion, health, or other sensitive attributes from photographs.

## 10. Weather and trends

Weather-sensitive advice requires reliable current weather data. If no weather source is connected, ask the user about conditions or give general seasonal advice without claiming to know the forecast.

Trend information changes over time. Unless the application has a current, trustworthy trend source, do not describe a recommendation as the latest trend. Focus on stable coordination principles instead.

## 11. Retrieval summary

Use this document when implementing preference-aware prompts, deciding which context matters, handling conflicts, choosing when to ask follow-up questions, and keeping recommendations respectful and grounded.
