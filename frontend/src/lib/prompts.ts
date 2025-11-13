// Importerer rå tekst via alias + ?raw
import contextPrompt from "@shared/prompts/context_prompt.txt?raw";
import managePrompt from "@shared/prompts/manage_prompt.txt?raw";
import researchPrompt from "@shared/prompts/research_prompt.txt?raw";

export const CONTEXT_PROMPT = contextPrompt.trim();
export const MANAGE_PROMPT = managePrompt.trim();
export const RESEARCH_PROMPT = researchPrompt.trim();
