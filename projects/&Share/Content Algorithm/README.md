cat <<EOF > "projects/&Share/Content Algorithm/README.md"
# Share V3 – Feed Algorithm Design

Initial conceptual feed algorithm for Share V3 – complete vector scoring, feed logic, user onboarding logic, decay and boost logic all included. Pseudocode ready for future pipeline integration.

---

### Core Principles

1. **User-led feed tuning**, not platform-driven.
2. **Vector scoring** per content item based on multiple weighted signals.
3. **Decentralised feed construction** – the user can curate multiple feeds (Home, Watch) as swipeable stacks.
4. **Cross-platform sync** – connected accounts populate content pool (e.g. IG, Pinterest, TikTok, YouTube).
5. **Archived utility** – access saved, pinned, or favorite content across platforms in one place.

---

### Feed Scoring Vector

Each content item \(c_i\) receives a score based on:

\`\`\`
Score(c_i) = 
    w1 * engagement_score +
    w2 * recency_score +
    w3 * content_type_score +
    w4 * relevance_vector · user_vector +
    w5 * boost_factor -
    d * decay_factor
\`\`\`

- `engagement_score`: likes, comments, shares from connected users or platforms
- `recency_score`: how recent the content is (log-scaled decay)
- `content_type_score`: prioritisation for media type (video, image, link, text)
- `relevance_vector · user_vector`: vector dot product from AI-personalised content match
- `boost_factor`: applies to user’s own creations, business shares, side accounts, etc
- `decay_factor`: global decay applied based on scroll depth or elapsed time

---

### Onboarding Flow

1. User downloads the app
2. Prompts to import/link social accounts (optional auto-import)
3. Content sync: user content + feeds from linked accounts
4. Quick-tap onboarding interface:
   - Sliders or buttons like:
     - "More side hustle content"
     - "Less memes"
     - "Boost saved guitar videos"
     - "See Jay’s updates always"
5. Optional: setup Watch stacks (e.g. Fitness, Friends, Art)
6. AI engine tunes the default Home feed based on:
   - Their account history
   - Saved posts from IG/Pinterest
   - Pinned or liked content
   - What they create

---

### Notes

- Feed is modular and swipable: each pane is an AI-managed stack
- Each user’s feed algo is editable, viewable, and optionally shareable
- Designed to end doomscrolling and revive authentic, user-led sharing

EOF
