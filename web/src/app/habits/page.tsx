import type { Metadata } from "next";
import { HabitsBoard } from "@/components/HabitsBoard";

export const metadata: Metadata = { title: "Today" };

export default function HabitsPage() {
  return <HabitsBoard />;
}
