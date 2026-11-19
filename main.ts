// gta6-meme-x-01 entry program (Node 22, standard library only).
//
// The entry itself is a public post on X; the house reads the post
// directly and builds the dossier the judge sees. All this program
// has to do is hand over POST.json, which names the post's address,
// copying it from the repository into the output directory.

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? ".";
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outDir, { recursive: true });
copyFileSync(join(botDir, "POST.json"), join(outDir, "POST.json"));
console.log("POST.json copied to", outDir);
