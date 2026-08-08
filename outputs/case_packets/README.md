# Case Packets

This directory is reserved for curated representative decision-support packet copies.

The currently committed canonical integrated P4-05 packet is stored under the stage output directory:

- [`../p4_05/decision_support_packet.md`](../p4_05/decision_support_packet.md)
- [`../p4_05/decision_support_packet.json`](../p4_05/decision_support_packet.json)

The reviewer-facing operator interface generates case-specific packet and audit artifacts in its runtime workspace. Use the **Save / Resume** stage to export a resumable case bundle when those artifacts need to survive the Colab runtime.

A decision-support packet contains a **nonbinding** system recommendation. Final authority remains with the authorized human disposition.
