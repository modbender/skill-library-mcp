"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Upload, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { submissionCreateSchema, type SubmissionCreateInput } from "@/lib/validators";

export function SubmissionForm() {
  const router = useRouter();
  const [uploading, setUploading] = useState(false);
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [toolsInput, setToolsInput] = useState("");

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<SubmissionCreateInput>({
    resolver: zodResolver(submissionCreateSchema),
    defaultValues: {
      currency: "USD",
      proofType: "SCREENSHOT",
    },
  });

  const proofType = watch("proofType");

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/v1/upload", { method: "POST", body: formData });
      const json = await res.json();
      if (res.ok) {
        setUploadedUrl(json.data.url);
        setValue("proofUrl", json.data.url);
      } else {
        setSubmitError(json.error ?? "Upload failed");
      }
    } catch {
      setSubmitError("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  }

  async function onSubmit(data: SubmissionCreateInput) {
    setSubmitError(null);

    // Convert comma-separated tools string to array
    const tools = toolsInput
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    const payload = {
      ...data,
      ...(tools.length > 0 && { tools }),
    };

    try {
      const res = await fetch("/api/v1/submissions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const json = await res.json();

      if (res.ok) {
        router.push(`/submission/${json.data.id}`);
      } else {
        setSubmitError(json.error ?? "Submission failed");
      }
    } catch {
      setSubmitError("Something went wrong. Please try again.");
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {submitError && (
        <div className="border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
          {submitError}
        </div>
      )}

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="openclawInstanceId">Instance ID</Label>
          <Input
            id="openclawInstanceId"
            placeholder="e.g. molty-42-abc123"
            {...register("openclawInstanceId")}
          />
          {errors.openclawInstanceId && (
            <p className="text-xs text-destructive">
              {errors.openclawInstanceId.message}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="openclawName">Display Name</Label>
          <Input
            id="openclawName"
            placeholder="e.g. Molty-42"
            {...register("openclawName")}
          />
          {errors.openclawName && (
            <p className="text-xs text-destructive">
              {errors.openclawName.message}
            </p>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">How did your OpenClaw earn this money?</Label>
        <Textarea
          id="description"
          placeholder="Describe the task, client, and outcome..."
          rows={4}
          {...register("description")}
        />
        {errors.description && (
          <p className="text-xs text-destructive">{errors.description.message}</p>
        )}
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="amountCents">Amount (in cents)</Label>
          <Input
            id="amountCents"
            type="number"
            placeholder="e.g. 5000 for $50.00"
            {...register("amountCents", { valueAsNumber: true })}
          />
          {errors.amountCents && (
            <p className="text-xs text-destructive">
              {errors.amountCents.message}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="currency">Currency</Label>
          <Select id="currency" {...register("currency")}>
            <option value="USD">USD ($)</option>
            <option value="EUR">EUR (&euro;)</option>
            <option value="GBP">GBP (&pound;)</option>
            <option value="BTC">BTC (&#8383;)</option>
            <option value="ETH">ETH (&Xi;)</option>
          </Select>
          {errors.currency && (
            <p className="text-xs text-destructive">{errors.currency.message}</p>
          )}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="proofType">Proof Type</Label>
        <Select id="proofType" {...register("proofType")}>
          <option value="SCREENSHOT">Screenshot</option>
          <option value="LINK">Link</option>
          <option value="TRANSACTION_HASH">Transaction Hash</option>
          <option value="DESCRIPTION_ONLY">Description Only</option>
        </Select>
      </div>

      {proofType === "SCREENSHOT" && (
        <div className="space-y-2">
          <Label>Upload Screenshot</Label>
          <div className="flex items-center gap-4">
            <label className="flex cursor-pointer items-center gap-2 border border-dashed border-border px-4 py-3 text-sm text-muted-foreground hover:border-primary/50 hover:text-foreground transition-colors">
              {uploading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Upload className="h-4 w-4" />
              )}
              {uploading
                ? "Uploading..."
                : uploadedUrl
                  ? "Replace screenshot"
                  : "Choose file"}
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                className="hidden"
                onChange={handleFileUpload}
                disabled={uploading}
              />
            </label>
            {uploadedUrl && (
              <span className="text-xs text-success">Uploaded</span>
            )}
          </div>
          <input type="hidden" {...register("proofUrl")} />
        </div>
      )}

      {proofType === "LINK" && (
        <div className="space-y-2">
          <Label htmlFor="proofUrl">Proof URL</Label>
          <Input
            id="proofUrl"
            type="url"
            placeholder="https://..."
            {...register("proofUrl")}
          />
          {errors.proofUrl && (
            <p className="text-xs text-destructive">{errors.proofUrl.message}</p>
          )}
        </div>
      )}

      {proofType === "TRANSACTION_HASH" && (
        <div className="space-y-2">
          <Label htmlFor="transactionHash">Transaction Hash</Label>
          <Input
            id="transactionHash"
            placeholder="0x..."
            {...register("transactionHash")}
          />
          {errors.transactionHash && (
            <p className="text-xs text-destructive">
              {errors.transactionHash.message}
            </p>
          )}
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="proofDescription">Additional Proof Details (optional)</Label>
        <Textarea
          id="proofDescription"
          placeholder="Any additional context about the proof..."
          rows={3}
          {...register("proofDescription")}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="verificationMethod">
          How can others verify this earning?
        </Label>
        <Textarea
          id="verificationMethod"
          placeholder="e.g. Check the Stripe dashboard at..., or verify the transaction on Etherscan..."
          rows={3}
          {...register("verificationMethod")}
        />
        {errors.verificationMethod && (
          <p className="text-xs text-destructive">
            {errors.verificationMethod.message}
          </p>
        )}
      </div>

      <details className="border border-border">
        <summary className="cursor-pointer px-4 py-3 text-sm font-medium select-none">
          Agent Configuration (optional)
        </summary>
        <div className="space-y-4 px-4 pb-4 pt-2">
          <div className="space-y-2">
            <Label htmlFor="systemPrompt">System Prompt</Label>
            <Textarea
              id="systemPrompt"
              placeholder="The system prompt / instructions given to the agent..."
              rows={6}
              {...register("systemPrompt")}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="modelProvider">Model Provider</Label>
              <Input
                id="modelProvider"
                placeholder='e.g. "Anthropic"'
                {...register("modelProvider")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="modelId">Model ID</Label>
              <Input
                id="modelId"
                placeholder='e.g. "claude-sonnet-4-5-20250929"'
                {...register("modelId")}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="toolsInput">Tools / APIs</Label>
            <Input
              id="toolsInput"
              placeholder="Comma-separated, e.g. web_search, code_execution, file_read"
              value={toolsInput}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setToolsInput(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Separate tool names with commas
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="configNotes">Config Notes</Label>
            <Textarea
              id="configNotes"
              placeholder="Any additional notes about the agent configuration..."
              rows={3}
              {...register("configNotes")}
            />
          </div>
        </div>
      </details>

      <Button type="submit" disabled={isSubmitting} className="w-full gap-2">
        {isSubmitting ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : null}
        {isSubmitting ? "Submitting..." : "Submit Earning"}
      </Button>
    </form>
  );
}
