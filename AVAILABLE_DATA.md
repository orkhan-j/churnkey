# 📊 Churnkey API - Available Data & Dashboard Ideas

## 🔌 API Endpoints

### 1. `/sessions` - Individual Session Data
Get detailed information about each cancellation flow session.

### 2. `/session-aggregation` - Aggregated Analytics
Get pre-aggregated counts by various breakdowns (month, week, region, etc.)

---

## 📋 Available Data Fields

### **Session Identification**
- `_id` - Unique session ID
- `org` - Organization ID
- `blueprintId` - Flow blueprint ID
- `segmentId` - Customer segment ID
- `createdAt` - Session timestamp
- `updatedAt` - Last update timestamp

### **Customer Information**
- `customer.id` - Customer ID (e.g., Stripe customer)
- `customer.email` - Customer email
- `customer.created` - Customer creation date
- `customer.subscriptionId` - Subscription ID
- `customer.subscriptionStart` - When subscription started
- `customer.subscriptionPeriodStart` - Current period start
- `customer.subscriptionPeriodEnd` - Current period end
- `customer.currency` - Currency (e.g., "usd")
- `customer.planId` - Price/plan ID
- `customer.planPrice` - Plan price in cents (e.g., 2500 = $25)
- `customer.itemQuantity` - Subscription quantity
- `customer.billingInterval` - "MONTH", "YEAR", etc.
- `customer.billingIntervalCount` - Number of intervals

### **Geographic/Regional Data**
- `region.matchedRegion` - Country name (e.g., "Israel", "United States")
- `region.matchedRegionCode` - Country code (e.g., "IL", "US")
- `region.clickToCancel` - Whether click-to-cancel is enabled
- `region.strictFTCCompliance` - FTC compliance mode

### **Session Outcome**
- `canceled` - Boolean: Did customer cancel?
- `aborted` - Boolean: Did customer abort the flow?
- `saveType` - Type of save: "DISCOUNT", "PAUSE", "PLAN_CHANGE", "ABANDON", null
- `usedClickToCancel` - Boolean: Used one-click cancel?

### **Survey/Feedback Data**
- `surveyId` - Survey question ID
- `surveyChoiceId` - Selected choice ID
- `surveyChoiceValue` - Selected reason (e.g., "Technical Issues", "Budget", "Not Needed Right Now")
- `feedback` - Free-form feedback text
- `followupQuestion` - Follow-up question shown
- `followupResponse` - Customer's follow-up response

### **Offers Presented**
Array of offers shown to customer:
- `presentedOffers[].guid` - Offer ID
- `presentedOffers[].accepted` - Boolean: Was it accepted?
- `presentedOffers[].presentedAt` - When shown
- `presentedOffers[].declinedAt` - When declined
- `presentedOffers[].offerType` - "DISCOUNT", "PAUSE", "PLAN_CHANGE", "REDIRECT", etc.
- `presentedOffers[].discountConfig` - Discount details (coupon, amount, duration)
- `presentedOffers[].redirectConfig` - Redirect URL and label
- `presentedOffers[].surveyOffer` - Boolean: Survey-triggered offer?

### **Flow Steps Viewed**
Array of steps in the cancellation flow:
- `stepsViewed[].guid` - Step ID
- `stepsViewed[].stepType` - "OFFER", "SURVEY", "FREEFORM", "CONFIRM", etc.
- `stepsViewed[].start` - When step started
- `stepsViewed[].end` - When step ended
- `stepsViewed[].duration` - Time spent (seconds)
- `stepsViewed[].numChoices` - Number of choices (for survey)

### **Sentiment Analysis** (AI-Powered)
Emotion scores for feedback:
- `sentimentScores.emotionA` - Primary emotions: angry, practical, confused, grateful
- `sentimentScores.emotionB` - Secondary emotions
- `sentimentScores.reasonA` - Reasons: need, budget, ease, refund, feature, technical
- `sentimentScores.reasonB` - Secondary reasons
- `sentimentScores.reactivateA` - Likelihood to reactivate (negative vs reactivate)
- `sentimentScores.productA` - Product sentiment (negative vs positive)
- `sentimentScores.productB` - Recommendation likelihood
- `sentimentScores.productC` - Product rating (poor vs great)
- `sentimentScores.productD` - Product feelings (dislike, like, hate, love)
- `sentimentScores.subjectiveA` - Feedback type (emotional vs reasonable)

### **Feedback Analysis**
- `feedbackAnalysis.feedbackTypes` - Categorized feedback types
- `feedbackAnalysis.timestamp` - Analysis timestamp
- `feedbackAnalysis.feedbackAnalyzerVersion` - Analysis version

### **Optimization & Settings**
- `autoOptimizationUsed` - Boolean: AI optimization enabled?
- `autoOptimizationKey` - Optimization segment key
- `discountCooldown` - Discount cooldown period
- `discountCooldownApplied` - Boolean: Cooldown applied?
- `pauseCooldown` - Pause cooldown period
- `pauseCooldownApplied` - Boolean: Cooldown applied?
- `managedFlow` - Boolean: Managed by Churnkey?
- `mode` - "LIVE" or "TEST"

### **Localization**
- `detectedLang` - Detected language (e.g., "en-US")
- `overriddenLang` - Language override
- `uiLang` - UI language used
- `contentLang` - Content language used
- `translationType` - "ai" or "manual"
- `availableTranslations` - Boolean: Translations available?

### **Recording**
- `recording` - URL to session recording JSON
- `recordingStartTime` - Recording start
- `recordingEndTime` - Recording end

### **Provider**
- `provider` - Payment provider (e.g., "STRIPE")

---

## 💡 Potential Dashboard Ideas

### 1. **Offer Performance Dashboard** ⭐
**What to track:**
- Acceptance rate by offer type (DISCOUNT vs PAUSE vs PLAN_CHANGE)
- Average time to accept/decline offers
- Revenue saved per offer type
- Discount amounts vs acceptance rates
- Most effective discount durations

**Visualizations:**
- Bar chart: Acceptance rate by offer type
- Line chart: Offer performance over time
- Table: Offer type breakdown with metrics

---

### 2. **Customer Sentiment Dashboard** 🎭
**What to track:**
- Emotion breakdown (angry, confused, grateful, practical)
- Sentiment scores over time
- Correlation between emotions and cancellation
- Product sentiment (positive vs negative)
- Likelihood to reactivate based on sentiment

**Visualizations:**
- Pie chart: Emotion distribution
- Sentiment trend over time
- Heat map: Sentiment by cancellation reason

---

### 3. **Geographic Analysis Dashboard** 🌍
**What to track:**
- Cancellation rates by country
- Acceptance rates by region
- Revenue impact by geography
- Click-to-cancel usage by country
- Popular cancellation reasons by region

**Visualizations:**
- World map: Cancellation rates
- Table: Top countries by cancellations
- Regional comparison charts

---

### 4. **Cancellation Reason Deep Dive** 🔍
**What to track:**
- Top cancellation reasons over time
- Reason trends (growing vs declining)
- Free-form feedback analysis
- Follow-up responses by reason
- Correlation between reason and offer acceptance

**Visualizations:**
- Word cloud: Free-form feedback
- Bar chart: Reason breakdown
- Trend lines: Reason changes over time
- Table: Reasons with example feedback

---

### 5. **Flow Optimization Dashboard** ⚡
**What to track:**
- Average time spent per step
- Drop-off points in the flow
- Steps with highest engagement
- Abort rate by step
- Survey completion rates

**Visualizations:**
- Funnel chart: Flow progression
- Time analysis: Duration per step
- Drop-off analysis

---

### 6. **Revenue Impact Dashboard** 💰
**What to track:**
- Revenue saved vs lost over time
- Revenue saved per customer segment
- Average plan price for canceled vs saved
- Monthly Recurring Revenue (MRR) impact
- Lifetime value saved

**Visualizations:**
- Stacked area: Saved vs lost revenue
- Comparison: Revenue by save type
- Trend: MRR impact over time

---

### 7. **Subscription Analysis Dashboard** 📅
**What to track:**
- Churn by billing interval (monthly vs annual)
- Cancellation timing (days into subscription)
- Plan tier analysis
- Subscription age at cancellation
- Renewal vs new customer cancellations

**Visualizations:**
- Histogram: Days to cancellation
- Comparison: Monthly vs annual churn
- Cohort analysis: Retention by plan

---

### 8. **AI Optimization Performance** 🤖
**What to track:**
- AI optimization vs manual performance
- Optimization key segments
- Save rates with vs without optimization
- A/B test results
- Discount auto-optimization effectiveness

**Visualizations:**
- Comparison: Optimized vs non-optimized
- Performance by segment
- ROI of AI features

---

### 9. **Customer Journey Timeline** 🛤️
**What to track:**
- Session duration analysis
- Time from start to decision
- Offer sequence effectiveness
- Recording replay insights
- Customer behavior patterns

**Visualizations:**
- Timeline view: Average session flow
- Duration histogram
- Step sequence analysis

---

### 10. **Feedback Intelligence Dashboard** 💬
**What to track:**
- Feedback sentiment scores
- Text analysis of free-form responses
- Common themes and keywords
- Feedback types categorization
- Actionable insights extraction

**Visualizations:**
- Word cloud: Common terms
- Sentiment distribution
- Theme breakdown
- Priority issues table

---

### 11. **Cooldown & Policy Impact** ⏱️
**What to track:**
- Cooldown application rates
- Impact of cooldowns on behavior
- Policy compliance by region
- Click-to-cancel adoption
- FTC compliance metrics

**Visualizations:**
- Cooldown effectiveness
- Regional policy comparison
- Compliance trends

---

### 12. **Win-Back Opportunity Dashboard** 🎯
**What to track:**
- Reactivation potential scores
- Customers likely to return
- Win-back campaign targets
- Sentiment-based segmentation
- Follow-up opportunity analysis

**Visualizations:**
- Reactivation likelihood distribution
- Target customer lists
- Segmentation by win-back potential

---

## 🎨 Advanced Dashboard Ideas

### **Multi-Dimensional Analysis**
Combine multiple factors:
- Cancellation reason × Geography × Plan tier
- Sentiment × Offer type × Time spent
- Save type × Customer age × Revenue

### **Predictive Dashboards**
Use historical data to predict:
- Churn risk by customer segment
- Optimal offer recommendations
- Best timing for interventions
- Revenue forecast from saves

### **Real-Time Monitoring**
- Live cancellation tracking
- Alert when churn spikes
- Real-time sentiment monitoring
- Instant feedback notifications

---

## 📊 Current Dashboards Built

1. ✅ **Acceptance Rates Dashboard** - Weekly/monthly acceptance tracking
2. ✅ **Cancellation Flow Dashboard** - Cancellation rates and top reasons

## 🚀 Recommended Next Dashboards

Based on the available data, I recommend building:

1. **Geographic Analysis Dashboard** - See which countries have highest churn
2. **Offer Performance Dashboard** - Optimize which offers to show
3. **Sentiment Analysis Dashboard** - Understand customer emotions
4. **Revenue Impact Dashboard** - Financial analysis of churn prevention

---

## 💾 Data Export Options

All data can be:
- Exported to CSV for offline analysis
- Queried via API for custom dashboards
- Aggregated by various dimensions
- Filtered by date ranges, segments, regions, etc.

---

**Need a specific dashboard?** Let me know which of these interests you and I'll build it!
