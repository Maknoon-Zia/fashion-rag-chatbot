# Skin Tone and Color Guidance

**Document ID:** fashion-complexion-002  
**Category:** complexion_guidance  
**Content type:** styling_guide  
**Audience:** all genders  
**Language:** English  
**Purpose:** Explain how complexion and color preference may inform clothing-color suggestions without making rigid or unsupported claims.

## 1. Key terms

**Terminology note:** In this knowledge base, "skin tone" and "complexion" are used interchangeably to mean the overall visible color of a person's skin. "Skin depth" describes how light or deep that color appears, and "undertone" describes a subtle warm, cool, or neutral quality. These are separate ideas.

### 1.1 Skin depth

Skin depth describes how light or deep a person's complexion appears. Common descriptive terms include fair, light, medium, tan, deep, and very deep. These labels are approximate and can vary across cultures and individuals.

### 1.2 Undertone

Undertone describes a subtle warm, cool, or neutral quality sometimes perceived beneath the surface color of skin.

- **Warm undertone:** may appear golden, peach, or yellowish.
- **Cool undertone:** may appear pink, rosy, or bluish.
- **Neutral undertone:** may show a mixture of warm and cool qualities or no strong obvious direction.

Undertone is not the same as skin depth. Two people with similar skin depth can have different undertones.

### 1.3 Surface appearance and lighting

Lighting, camera white balance, makeup, sun exposure, and the surrounding colors can change how complexion appears in a photograph. A single image is not a reliable basis for making a definitive claim about a person's undertone.

## 2. General color suggestions

The following are starting points for trying colors, not rules that determine what a person can or cannot wear.

### 2.1 Warm-leaning palettes

Colors often described as warm include rust, terracotta, warm olive, mustard, coral, warm brown, and some creamy neutrals. A person who enjoys warm palettes may test these shades near the face and compare them in natural light.

### 2.2 Cool-leaning palettes

Colors often described as cool include blue, blue-green, berry, plum, some pinks, and cool grey. These can be tested against the user's preferred level of brightness and contrast.

### 2.3 Neutral palettes

Black, white, grey, cream, beige, taupe, and many browns can be used as a base. The exact shade matters: a warm cream and a stark white create different effects, and a grey can lean warm or cool.

### 2.4 Deep and saturated colors

Deep green, burgundy, cobalt, plum, and other saturated shades can create a strong visual effect. Whether a particular shade feels flattering depends on the person's preference, contrast, fabric, and the rest of the outfit. Avoid claiming that all people within one skin-depth category should wear the same colors.

## 3. A practical method for choosing colors

1. Select two or three candidate colors.
2. View each color near the face in consistent natural light, if possible.
3. Compare how the person feels about the overall effect and whether they prefer a softer or stronger contrast.
4. Consider the actual garment, fabric, and occasion.
5. Ask the user which option they prefer and treat that preference as meaningful evidence.

A styling assistant should offer choices and explain trade-offs rather than declaring a color unsuitable based only on skin tone.

## 4. Example scenarios

### Scenario A: User asks for colors for a tan complexion

A useful response might offer forest green, burgundy, teal, cream, charcoal, and selected earthy shades as options to try. It should explain that these are starting points and ask whether the user prefers rich contrast, muted colors, or lighter shades. It should not imply that all tan complexions are identical.

### Scenario B: User asks whether black suits them

Black is a versatile neutral and can be styled in many ways. If the user finds solid black too stark, options include adding a softer scarf near the face, choosing textured black fabric, or introducing a color they enjoy. The assistant should not say that black is categorically wrong for a particular complexion.

### Scenario C: User wants a hijab color

Ask about the main outfit color and desired effect. For a black outfit, possible choices include cream for contrast, dusty green for a muted accent, burgundy for richness, or blue-grey for a cooler palette. The best recommendation depends on the user's preferences and available pieces.

## 5. Responsible use of complexion information

- Do not rank skin tones or describe one complexion as better than another.
- Do not infer ethnicity, identity, health, or personality from skin color.
- Do not treat an image-based undertone estimate as certain.
- Do not claim that complexion alone determines the best outfit.
- Allow users to override any general suggestion.
- Ask for clarification if the image or description is ambiguous.
- Do not use skin tone as a substitute for learning a user's stated color preferences.

## 6. Suggested structured attributes

If an application stores optional styling preferences, useful fields may include:
- `skin_depth_preference`: optional user-described category;
- `undertone_preference`: warm, cool, neutral, unsure, or not provided;
- `preferred_colors`: list of colors the user likes;
- `avoid_colors`: list of colors the user wants to avoid;
- `contrast_preference`: low, medium, high, or not specified.

These should be optional user preferences, not mandatory demographic labels. Store only what is necessary and allow the user to edit or remove it.

## 7. Retrieval summary

Use this document for questions about complexion-aware styling, undertones, colors for tan or deep skin, hijab or scarf color choices near the face, and responsible personalization. Responses should be flexible, non-judgmental, and clear about uncertainty.
