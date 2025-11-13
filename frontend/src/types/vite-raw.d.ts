// Gør det muligt at importere tekstfiler som string via ?raw
declare module "*.txt?raw" {
  const content: string;
  export default content;
}
