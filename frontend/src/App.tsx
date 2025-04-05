import {
  Box,
  Button,
  FileUpload,
  Field,
  Skeleton,
  HStack,
  ClientOnly,
  Heading,
  Progress,
  VStack,
  Clipboard,
  IconButton,
  Link,
} from "@chakra-ui/react";
import { RiGithubLine } from "react-icons/ri";

import { ColorModeToggle } from "./components/color-mode-toggle";
import { HiUpload } from "react-icons/hi";
import { Input } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import axios from "axios";
import { Toaster, toaster } from "./components/ui/toaster";

export default function Page() {
  const [files, setFiles] = useState<File[]>([]);
  const [key, setKey] = useState<string>(localStorage.getItem("key") || "");
  const [progress, setProgress] = useState(0);
  const [link, setLink] = useState("");

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("auth", key);
    // only one file per upload
    files.forEach((file) => {
      formData.append("file", file);
    });

    try {
      const res = await axios.post("/api/upload", formData, {
        onUploadProgress: (progressEvent) => {
          setProgress((progressEvent.progress as number) * 100);
        },
      });
      setLink(res.data.link);
      toaster.create({
        title: "Upload finish!",
        type: "success",
      });
    } catch (e: any) {
      toaster.create({
        title: e.response.data.message,
        type: "error",
      });
    }
  };

  useEffect(() => {
    // get query argument from url `key` and set it to key
    const urlParams = new URLSearchParams(window.location.search);
    const keyFromUrl = urlParams.get("key");
    if (keyFromUrl) {
      setKey(keyFromUrl);
      localStorage.setItem("key", keyFromUrl);
    }
  }, []);

  return (
    <Box textAlign="center" fontSize="xl" pt="10vh">
      <Toaster />
      <VStack gap="8">
        <img alt="chakra logo" src="/static/logo.png" width="80" height="80" />
        <Heading size="2xl" letterSpacing="tight">
          新疆大盘鸡
        </Heading>
        {link && (
          <Clipboard.Root value="https://chakra-ui.com">
            <Clipboard.Trigger asChild>
              <Link as="span" color="blue.fg" textStyle="sm">
                <Clipboard.Indicator />
                <Clipboard.ValueText />
              </Link>
            </Clipboard.Trigger>
          </Clipboard.Root>
        )}
        <HStack gap="6" justify="center">
          <Field.Root required>
            <Input
              placeholder="Enter your API Key"
              value={key}
              onChange={(e) => {
                setKey(e.target.value);
                localStorage.setItem("key", e.target.value);
              }}
            />
          </Field.Root>

          <FileUpload.Root
            onFileAccept={(details) => {
              setFiles(details.files);
            }}
          >
            <FileUpload.HiddenInput />
            <FileUpload.Trigger asChild>
              <Button variant="outline" size="sm">
                <HiUpload /> Select file
              </Button>
            </FileUpload.Trigger>
            <FileUpload.List showSize clearable />
          </FileUpload.Root>
        </HStack>

        {!!progress && (
          <Progress.Root
            width="30%"
            size="lg"
            colorPalette="teal"
            value={progress}
          >
            <Progress.Label mb="2">
              {progress < 100 ? "Uploading" : "Uploaded"}
            </Progress.Label>
            <Progress.Track>
              <Progress.Range />
            </Progress.Track>
          </Progress.Root>
        )}

        <Button onClick={handleUpload} disabled={files.length === 0}>
          Upload
        </Button>
      </VStack>
      <Box pos="absolute" top="4" right="4">
        <VStack>
          <ClientOnly fallback={<Skeleton w="10" h="10" rounded="md" />}>
            <ColorModeToggle />
          </ClientOnly>
          <IconButton
            aria-label="opensource"
            onClick={() => {
              window.location.href = "https://github.com/BennyThink/xjdpj";
            }}
          >
            <RiGithubLine />
          </IconButton>
        </VStack>
      </Box>
    </Box>
  );
}
