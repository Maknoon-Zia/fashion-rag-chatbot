# Styling Examples and Recommendation Reasoning

**Document ID:** fashion-examples-008  
**Category:** styling_examples  
**Content type:** example_library  
**Audience:** all genders  
**Language:** English  
**Purpose:** Provide self-contained scenarios that can be used to test retrieval and grounded answer generation in a fashion RAG system.

## How to use these examples

These examples illustrate general styling reasoning. They are not a dataset of objectively correct fashion judgments. In a RAG application, retrieve the relevant example as supporting context, then adapt the recommendation to the user's actual preferences and constraints. Do not copy an example blindly when the user's situation differs.

## Example 1: Men's office outfit

**User request:** "Suggest a simple outfit for an office day. I have charcoal trousers."

**Relevant context:** Office and business-casual guidance; color coordination; menswear.

**Recommendation:** Pair the charcoal trousers with a white or light blue collared shirt. Choose clean black or dark brown shoes according to the workplace dress code. If wearing a belt, coordinate it with the shoes where practical. A simple watch is optional.

**Reasoning:** Charcoal is a versatile neutral. White or light blue creates a restrained upper-body color, while understated footwear keeps the outfit appropriate for many office environments.

**Personalization check:** If the office requires a suit or traditional clothing, adapt the suggestion to that requirement.

## Example 2: Suit and tie coordination

**User request:** "What tie can I wear with a charcoal suit and white shirt?"

**Recommendation:** Burgundy is one option for a rich accent. Deep green, muted blue, or a restrained patterned tie may also work depending on the event and preference.

**Reasoning:** The charcoal suit and white shirt form a neutral base, so the tie can introduce controlled color. A simple tie is often easier to coordinate with a strongly patterned shirt; here the white shirt allows more flexibility.

**Limitation:** The best option depends on the occasion, tie pattern, and the user's taste.

## Example 3: Black abaya and hijab

**User request:** "I wear a black abaya. Suggest a hijab color for university."

**Recommendation:** Cream creates clear contrast; dusty green gives a muted color accent; burgundy feels richer; blue-grey creates a cooler palette. Choose comfortable footwear and a practical bag suitable for a full day on campus.

**Reasoning:** Black acts as a neutral base, so several scarf colors can work. The choice depends on whether the user prefers contrast, a muted look, or a deeper accent.

**Personalization check:** If the user dislikes one of these colors, remove it from future suggestions rather than repeating it.

## Example 4: Outfit for a wedding guest

**User request:** "I need a festive outfit for a wedding."

**Recommendation:** Start by checking the wedding's dress code and cultural context. One possible palette is deep green with cream or champagne details, with accessories chosen to complement the garment's embellishment. Select footwear suitable for the venue and expected duration.

**Reasoning:** Deep green and light metallic or cream details can create a festive contrast. The level of embellishment should reflect the event and the user's role.

**Limitation:** Do not assume that a particular color is appropriate for every wedding. Ask about any stated color restrictions if needed.

## Example 5: Everyday outfit with limited items

**User request:** "I only have black trousers, a white top, and sneakers. How can I style them?"

**Recommendation:** Use the black trousers and white top as the base. Add a lightweight jacket, cardigan, scarf, or bag if available. Keep the sneakers clean and suitable for the activity.

**Reasoning:** Black and white create a simple high-contrast base. An optional third item can introduce color or texture without requiring a new complete outfit.

**Personalization check:** Do not recommend buying items if the user has asked to use only what they own.

## Example 6: Complexion-aware color request

**User request:** "I have a tan complexion. Which colors should I try?"

**Recommendation:** Consider trying forest green, burgundy, teal, cream, charcoal, or selected earthy shades. Compare a few options near the face in consistent natural light and choose those the user likes.

**Reasoning:** These colors offer different combinations of depth, warmth, and contrast. Skin depth alone does not determine the most suitable color.

**Limitation:** Do not claim that all people with tan complexions share the same undertone or that any color is forbidden.

## Example 7: Patterned garment

**User request:** "My kurta has a colorful print. What dupatta should I choose?"

**Recommendation:** Choose a plain dupatta in one of the colors already present in the print, or select a neutral that suits the outfit. If the print is visually bold, a simpler dupatta may help keep the outfit balanced.

**Reasoning:** Repeating one color from the print creates a connection between pieces. A neutral can reduce visual complexity.

**Personalization check:** If the user wants a bold, layered look, a second pattern can be considered instead of automatically avoiding it.

## Example 8: Gold or silver accessories

**User request:** "Should I wear gold or silver jewelry with my outfit?"

**Recommendation:** Consider the garment's colors, embellishments, event, and the user's preferred metal. Gold-toned jewelry can create a warm accent; silver-toned jewelry can create a cooler effect. Either can work with many palettes.

**Reasoning:** Metallic accessories contribute tone and visual emphasis, but there is no universal rule requiring a particular metal for a particular complexion.

## Example 9: User dislikes the usual recommendation

**User request:** "I need a formal outfit, but I don't like navy."

**Recommendation:** Consider charcoal, black, grey, forest green, or burgundy depending on the garment and occasion. For example, charcoal trousers with a white shirt and black shoes can create a restrained formal look.

**Reasoning:** A styling system should honor explicit dislikes. Versatility is not a reason to keep recommending a color the user has rejected.

## Example 10: Weather-sensitive request without live weather data

**User request:** "Suggest an outfit for an outdoor event tomorrow."

**Recommendation:** Ask about the expected temperature or provide a general outfit with layers that can be adjusted. Choose footwear suitable for the venue and walking conditions.

**Reasoning:** Outdoor comfort depends on actual conditions and activity.

**Limitation:** If the application has no live weather integration, it must not invent tomorrow's forecast.

## Example 11: Insufficient evidence in the knowledge base

**User request:** "Which exact outfit will guarantee that everyone thinks I look fashionable?"

**Recommendation:** Explain that no outfit can guarantee everyone's opinion. Offer to suggest a coordinated look based on the occasion, preferred style, available clothing, and desired effect.

**Reasoning:** Fashion judgments vary between people and contexts. The assistant should provide useful options without promising a universal outcome.

## Example 12: User asks for a brand-specific current trend

**User request:** "What is the newest collection from a particular fashion brand?"

**Recommendation:** State that the current collection needs a reliable, up-to-date source. If the application does not have browsing or a current brand catalogue, ask the user to provide a source or explain that the knowledge base may not contain recent information.

**Reasoning:** A static styling knowledge base cannot establish current product availability or the newest collection by itself.

## Suggested evaluation questions

Use these questions to check whether retrieval returns relevant passages:

1. How can I coordinate a charcoal suit with a white shirt?
2. What scarf colors could work with a black abaya?
3. What is the difference between skin depth and undertone?
4. How should I coordinate a tie, belt, and shoes?
5. How can I style a colorful printed kurta?
6. What should I consider when choosing an outfit for an interview?
7. How can I make several outfits from black trousers?
8. What should the assistant do if the user dislikes navy?
9. Can the assistant know tomorrow's weather without a weather source?
10. What should the assistant say when its knowledge base cannot support an answer?

## Expected system behavior

A well-behaved RAG system should:
- retrieve passages that directly address the user's question;
- use user preferences and occasion details when available;
- distinguish general guidance from certainty;
- provide explanations rather than unsupported judgments;
- cite document titles or source sections when the application supports citations;
- ask for missing information only when it materially changes the answer;
- say when the knowledge base does not contain enough information;
- avoid inventing current weather, current trends, brand details, or scientific claims.
