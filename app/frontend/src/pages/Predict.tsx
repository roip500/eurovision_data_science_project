import { useState, useEffect, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ComboInput } from "@/components/ui/combo-input";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, Target, Sparkles, TrendingUp } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface FormData {
  year: string;
  country: string;
  main_language: string;
  tone: string;
  broadcaster: string;
  bpm: string;
  dancers: string;
  running_order: string;
  lyrics_text: string;
  top_k: number;
}

type HealthResp = {
  available_models: {
    [k: string]: string[]; // e.g. {"1":["lr","hgb","ensemble"], "2":[...]}
  };
};

type PredictResp = {
  top_k: number;
  probabilities: Record<string, number>; // lr_text_tab, hgb_tabular, ensemble
  threshold: number;
  decisions: Record<string, number>;
  explanations?: any;
  models_available: string[];
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const countries = [
  { value: "SE", label: "Sweden" },
  { value: "IT", label: "Italy" },
  { value: "UK", label: "United Kingdom" },
  { value: "DE", label: "Germany" },
  { value: "FR", label: "France" },
  { value: "ES", label: "Spain" },
  { value: "NL", label: "Netherlands" },
  { value: "AU", label: "Australia" },
  { value: "IL", label: "Israel" },
  { value: "UA", label: "Ukraine" },
];

const languages = [
  { value: "English", label: "English" },
  { value: "Native", label: "Native" },
  { value: "Mixed", label: "Mixed" },
  { value: "Other", label: "Other" }
];

const tones = [
  { value: "A major", label: "A major" },
  { value: "A minor", label: "A minor" },
  { value: "B major", label: "B major" },
  { value: "B minor", label: "B minor" },
  { value: "C major", label: "C major" },
  { value: "C minor", label: "C minor" },
  { value: "D major", label: "D major" },
  { value: "D minor", label: "D minor" },
  { value: "E major", label: "E major" },
  { value: "E minor", label: "E minor" },
  { value: "F major", label: "F major" },
  { value: "F minor", label: "F minor" },
  { value: "G major", label: "G major" },
  { value: "G minor", label: "G minor" }
];

const Predict = () => {
  const [searchParams] = useSearchParams();
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [predictions, setPredictions] = useState<PredictResp | null>(null);

  // NEW: model selection + threshold
  const [useModels, setUseModels] = useState<string[]>(["lr", "hgb", "ensemble"]);
  const [threshold, setThreshold] = useState<number>(0.5);
  // NEW: backend model availability (per K)
  const [availableByK, setAvailableByK] = useState<Record<number, string[]>>({});

  const [formData, setFormData] = useState<FormData>({
    year: "2024",
    country: "",
    main_language: "",
    tone: "",
    broadcaster: "",
    bpm: "",
    dancers: "",
    running_order: "",
    lyrics_text: "",
    top_k: 3,
  });

  // Fetch backend /health once
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/health`);
        if (!res.ok) throw new Error(`${res.status}`);
        const data: HealthResp = await res.json();
        const map: Record<number, string[]> = {};
        [1,2,3].forEach(k => {
          map[k] = data.available_models?.[String(k)] ?? [];
        });
        setAvailableByK(map);
      } catch {
        // If backend is down, just keep defaults; UI still works in "demo" mode
      }
    })();
  }, []);

  // Disable unavailable models for current K
  const availableForK = useMemo(() => {
    return availableByK[formData.top_k] ?? ["lr", "hgb", "ensemble"]; // optimistic default
  }, [availableByK, formData.top_k]);

  // Keep "ensemble" only if both lr & hgb are selected and available
  useEffect(() => {
    const hasLR = useModels.includes("lr") && availableForK.includes("lr");
    const hasHGB = useModels.includes("hgb") && availableForK.includes("hgb");
    if (!hasLR || !hasHGB) {
      setUseModels(prev => prev.filter(m => m !== "ensemble"));
    }
  }, [availableForK, useModels]);

  // Load demo data if demo=true in URL
  useEffect(() => {
    if (searchParams.get("demo") === "true") {
      setFormData({
        year: "2023",
        country: "SE",
        main_language: "English",
        tone: "A minor",
        broadcaster: "SVT",
        bpm: "128",
        dancers: "4",
        running_order: "18",
        lyrics_text: "We're dancing in the moonlight, feeling so alive tonight. Eurovision brings us all together, music makes us free forever.",
        top_k: 3,
      });
      toast({
        title: "Demo Loaded!",
        description: "Example Eurovision song data has been loaded for you to try.",
      });
    }
  }, [searchParams, toast]);

  const totalSteps = 4;
  const progress = (currentStep / totalSteps) * 100;

  const handleInputChange = (field: keyof FormData, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const canGoNext = () => {
    switch (currentStep) {
      case 1:
        return formData.year && formData.country;
      case 2:
        return formData.bpm !== "";
      case 3:
        return formData.lyrics_text.length > 0;
      case 4:
        return true;
      default:
        return false;
    }
  };

  const resetForm = () => {
    setFormData({
      year: "2024",
      country: "",
      main_language: "",
      tone: "",
      broadcaster: "",
      bpm: "",
      dancers: "",
      running_order: "",
      lyrics_text: "",
      top_k: 3,
    });
    setUseModels(["lr", "hgb", "ensemble"]);
    setThreshold(0.5);
  };

  // --- REAL backend call ---
  const handlePredict = async () => {
    setIsLoading(true);
    try {
      // build request body
      const body = {
        top_k: formData.top_k,
        use_models: useModels, // e.g., ["lr","hgb","ensemble"]
        threshold,
        features: {
          year: formData.year ? Number(formData.year) : null,
          country: formData.country || null,
          main_language: formData.main_language || null,
          tone: formData.tone || null,
          broadcaster: formData.broadcaster || null,
          bpm: formData.bpm ? Number(formData.bpm) : null,
          dancers: formData.dancers ? Number(formData.dancers) : null,
          running_order: formData.running_order ? Number(formData.running_order) : null,
          lyrics_text: formData.lyrics_text || "",
        },
      };

      const res = await fetch(`${API_BASE}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || `HTTP ${res.status}`);
      }

      const data: PredictResp = await res.json();
      setPredictions(data);

      toast({
        title: "Prediction Complete!",
        description: "Your Eurovision song has been analyzed by our ML models.",
      });
    } catch (error: any) {
      toast({
        title: "Prediction Failed",
        description: error?.message || "There was an error processing your request.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleModel = (m: "lr" | "hgb" | "ensemble") => {
    setUseModels(prev => {
      const has = prev.includes(m);
      if (has) return prev.filter(x => x !== m);
      return [...prev, m];
    });
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-4">Basic Information</h3>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="year">Year</Label>
                <Input
                  id="year"
                  type="number"
                  min="2000"
                  max="2030"
                  value={formData.year}
                  onChange={(e) => handleInputChange("year", e.target.value)}
                  placeholder="2024"
                />
              </div>

              <div>
                <Label htmlFor="country">Country</Label>
                <ComboInput
                  value={formData.country}
                  onValueChange={(value) => handleInputChange("country", value)}
                  options={countries}
                  placeholder="Select or type country"
                />
              </div>

              <div>
                <Label htmlFor="language">Main Language</Label>
                <ComboInput
                  value={formData.main_language}
                  onValueChange={(value) => handleInputChange("main_language", value)}
                  options={languages}
                  placeholder="Select or type language"
                />
              </div>

              <div>
                <Label htmlFor="tone">Tone</Label>
                <ComboInput
                  value={formData.tone}
                  onValueChange={(value) => handleInputChange("tone", value)}
                  options={tones}
                  placeholder="Select or type tone"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="broadcaster">Broadcaster (Optional)</Label>
              <Input
                id="broadcaster"
                value={formData.broadcaster}
                onChange={(e) => handleInputChange("broadcaster", e.target.value)}
                placeholder="e.g., SVT, BBC, RAI"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-4">Performance Details</h3>

            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="bpm">BPM</Label>
                <Input
                  id="bpm"
                  type="number"
                  min="60"
                  max="200"
                  value={formData.bpm}
                  onChange={(e) => handleInputChange("bpm", e.target.value)}
                  placeholder="120"
                />
              </div>

              <div>
                <Label htmlFor="dancers">Number of Dancers</Label>
                <Input
                  id="dancers"
                  type="number"
                  min="0"
                  max="20"
                  value={formData.dancers}
                  onChange={(e) => handleInputChange("dancers", e.target.value)}
                  placeholder="0"
                />
              </div>

              <div>
                <Label htmlFor="running_order">Running Order</Label>
                <Input
                  id="running_order"
                  type="number"
                  min="1"
                  max="26"
                  value={formData.running_order}
                  onChange={(e) => handleInputChange("running_order", e.target.value)}
                  placeholder="e.g., 15"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-4">Lyrics</h3>

            <div>
              <Label htmlFor="lyrics">Song Lyrics</Label>
              <Textarea
                id="lyrics"
                rows={10}
                value={formData.lyrics_text}
                onChange={(e) => handleInputChange("lyrics_text", e.target.value)}
                placeholder="Enter the complete song lyrics here..."
                className="min-h-[200px]"
              />
              <p className="text-sm text-muted-foreground mt-2">
                Words: {formData.lyrics_text.split(/\s+/).filter(word => word.length > 0).length} |
                {" "}Characters: {formData.lyrics_text.length}
              </p>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold mb-4">Prediction Settings</h3>

            <div>
              <Label>Top-K Setting</Label>
              <div className="flex gap-2 mt-2">
                {[1, 2, 3].map((k) => (
                  <Button
                    key={k}
                    variant={formData.top_k === k ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleInputChange("top_k", k)}
                  >
                    Top-{k}
                  </Button>
                ))}
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                Predict probability of finishing in the top {formData.top_k} positions
              </p>
            </div>

            <div className="space-y-2">
              <Label>Models</Label>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant={useModels.includes("lr") ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleModel("lr")}
                  disabled={!availableForK.includes("lr")}
                >
                  Logistic Regression
                </Button>
                <Button
                  variant={useModels.includes("hgb") ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleModel("hgb")}
                  disabled={!availableForK.includes("hgb")}
                >
                  Gradient Boosting
                </Button>
                <Button
                  variant={useModels.includes("ensemble") ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleModel("ensemble")}
                  disabled={
                    !availableForK.includes("ensemble") ||
                    !useModels.includes("lr") || !useModels.includes("hgb")
                  }
                >
                  Ensemble
                </Button>
              </div>
              {!availableByK[formData.top_k] && (
                <p className="text-xs text-muted-foreground">
                  (Tip: set <code>VITE_API_BASE_URL</code> to your backend and refresh)
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="threshold">Decision Threshold: {threshold.toFixed(2)}</Label>
              <input
                id="threshold"
                type="range"
                min={0}
                max={1}
                step={0.01}
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full"
              />
              <p className="text-sm text-muted-foreground">
                Used only for the optional 0/1 decision; probabilities are unaffected.
              </p>
            </div>

            <div className="pt-4">
              <Button
                onClick={handlePredict}
                disabled={isLoading || useModels.length === 0}
                size="lg"
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Sparkles className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing Song...
                  </>
                ) : (
                  <>
                    <Target className="mr-2 h-4 w-4" />
                    Get Predictions
                  </>
                )}
              </Button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (predictions) {
    const p = predictions.probabilities || {};
    const fmt = (x?: number) =>
      typeof x === "number" && isFinite(x) ? `${(x * 100).toFixed(1)}%` : "N/A";

    return (
      <div className="min-h-screen py-8">
        <div className="container mx-auto px-4 max-w-4xl">
          <Card className="eurovision-card-lg">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl flex items-center justify-center gap-2">
                <TrendingUp className="h-6 w-6 text-primary" />
                Prediction Results
              </CardTitle>
              <CardDescription>
                Top-{predictions.top_k} probability predictions for your Eurovision song
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              <div className="grid md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-muted-foreground">Logistic Regression</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-primary">
                      {fmt(p["lr_text_tab"])}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-muted-foreground">Gradient Boosting</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-secondary">
                      {fmt(p["hgb_tabular"])}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-muted-foreground">Ensemble</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-accent-foreground">
                      {fmt(p["ensemble"])}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="text-center pt-4">
                <Badge variant="outline" className="text-sm">
                  Top-{predictions.top_k} Prediction Complete (threshold {predictions.threshold.toFixed(2)})
                </Badge>
                <p className="text-sm text-muted-foreground mt-2">
                  Predictions are probabilities based on historical Eurovision data and cross-validated models.
                </p>
              </div>

              <div className="flex gap-4 pt-6">
                <Button
                  variant="outline"
                  onClick={() => {
                    setPredictions(null);
                    setCurrentStep(1);
                    resetForm();
                  }}
                  className="flex-1"
                >
                  New Prediction
                </Button>
                <Button
                  onClick={() => {
                    setPredictions(null);
                    setCurrentStep(4);
                  }}
                  className="flex-1"
                >
                  Modify Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        <Card className="eurovision-card-lg">
          <CardHeader>
            <div className="flex items-center justify-between mb-4">
              <CardTitle className="text-2xl">Eurovision Song Predictor</CardTitle>
              <Badge variant="outline">
                Step {currentStep} of {totalSteps}
              </Badge>
            </div>
            <Progress value={progress} className="w-full" />
            <CardDescription className="mt-2">
              Enter your song details to get Top-K probability predictions
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            {renderStep()}

            <div className="flex justify-between pt-6">
              <Button
                variant="outline"
                onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
                disabled={currentStep === 1}
              >
                <ChevronLeft className="mr-2 h-4 w-4" />
                Previous
              </Button>

              {currentStep < totalSteps && (
                <Button
                  onClick={() => setCurrentStep(Math.min(totalSteps, currentStep + 1))}
                  disabled={!canGoNext()}
                >
                  Next
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Predict;
