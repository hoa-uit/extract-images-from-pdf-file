import fs from "fs";
import path from "path";
import { getDocument, OPS } from "pdfjs-dist";
import sharp from "sharp";

const pdfPath = "lorem_picsum_2.pdf";
const outputDir = "extracted_images";

fs.mkdirSync(outputDir, { recursive: true });

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function extractImages() {
  const pdf = await getDocument(pdfPath).promise;
  const extractedImages = [];

  for (let i = 0; i < pdf.numPages; i++) {
    const page = await pdf.getPage(i + 1);
    const operatorList = await page.getOperatorList();
    const imageKeys = new Set();

    for (let j = 0; j < operatorList.fnArray.length; j++) {
      if (
        operatorList.fnArray[j] === OPS.paintImageXObject ||
        operatorList.fnArray[j] === OPS.paintInlineImageXObject
      ) {
        imageKeys.add(operatorList.argsArray[j][0]);
      }
    }

    // Ensure objects are resolved before accessing them
    await sleep(1000);
    await page.objs.ready;

    for (const imgKey of imageKeys) {
      const img = page.objs.get(imgKey) || page.commonObjs.get(imgKey);

      if (img && img.data) {
        let imgData = img.data;
        let ext = "png";

        const bytes = imgData.length;
        const channels = bytes / (img.width * img.height);
        const imgPath = path.join(
          outputDir,
          `page_${i + 1}_image_${imgKey}.${ext}`
        );

        await sharp(imgData, {
          raw: { width: img.width, height: img.height, channels },
        }).toFile(imgPath);

        extractedImages.push(imgPath);
      }
    }
  }

  console.log("Extracted images:", extractedImages);
}

extractImages().catch(console.error);
