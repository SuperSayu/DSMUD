We're moving back towards a D20-ish base mostly because the pure DSDice system didn't have enough randomness.  This actually manifests as D80//4, which has 3% 0 result and 1% 20-result, 4% for each 1-19.  With that done, we need to boost our DCs, but we can do so knowing that the overall dice result ceases to be an increasingly sharp bell curve as your skill goes up.  Thus, we can create a DC system that generally accounts for your increasing dice pool but without needing every single +2 result to be consequential.  We can also entirely eliminate the idea of rolling under the target DC to get success at a penalty.

I'd like to still make use of Stances, and probably expand that to Stance, Proficiency, Role, and Occupation, with roll DCs assuming generally 0-4 of those being a factor, depending on difficulty.  This will also be a factor for when higher dice are used; perhaps Mastery dice are used even when not rolling within your Role/Occupation, and Affinity dice are still rolled even when not rolling within your Stance.  When rolling outside of your Stance, Role, or Occupation, all Stat dice are Brute and all Affinity dice Slip.  Practice dice perhaps only apply if you keep rolling the same skill over and over again; you get a streak bonus capped to your Practice, only for skills within your Stance.  The streak bonus decays over time and resets to zero during any rest (or rests require decaying streaks before taking effect, training requires streaking up to that bonus before taking effect).

To counter the penalties, I expect that various actions, especially in combat, will have a free stance change effect.  Otherwise, stance changes are a time-consuming action, with more time consumed if you are in a deep streak.

Once a result has been rolled, bonuses should be a roll-under system, with target dice and max overage.  For example, if you get a +12 result capped at +8 and a d4 bonus die, you would roll d4, subtracting from 8 until you roll over:

8 - 1d4:1 = 7 +1b
7 - 1d4:4 = 3 +2b
3 - 1d4:1 = 2 +3b
2 - 1d4:4 => end with 3 bonuses

Stances, Professions, and Classes all let you combine skill rolls into your active skill checks.  Skill checks or skill definitions must specify what kind of skills can be used as "passive" skill checks for it, for example, Mining when attacking rock-type or burrowing enemies, or when using a Pickaxe as a weapon.

I feel like skill DCs should generally speaking be presuming double ranks: Untrained, Amateur, Professional, and Master, with Easy, Medium, and Hard of each rank (or more, Master/Grandmaster beyond hard?, Trivial beneath Easy?).  Each UAPM rank increases how much the EMH increases the roll, and adds its own increasing bonus DC.

What's important is setting up the system so that you can switch to be able to use a skill as long as you are willing to rest, with your Class and Profession accumulating skills that you want always available.  Your current stance can always be temporarily altered with rest, but you can swap to whole sets by fixing stances and setting them.  A set stance only needs to overwrite some of your currently slotted skills, but any automatic or passive effects are set by your current/new skills.

Generally, I suppose, a skillset has slots per aspect and a maximum number of skills in the set (determined by its level).  Perhaps, all skillsets combined cannot exceed one skill per attribute?  That may be restrictive.  Perhaps aspect level determines number of slots?  NOT FOR NOW

For now:
* Skill: Stat is baked in
* Skill: Internal momentum
* Skillcore: return status of a given skill
* Skill roll: Factor in skill status and momentum in dice selection
** Active (Stance)
** Standby (No stance): Aff/Momentum=Slip, Stat/Momentum->Brute, Training/Momentum->None
** Inactive (No Class): Mast=Mast,
* Command: Equip skill in current stance
* Command: Show stance

Perhaps before that, cleanup skillcore and statcore with APs/SPs?