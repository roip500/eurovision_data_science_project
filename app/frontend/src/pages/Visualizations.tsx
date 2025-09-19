import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { BarChart, LineChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { BarChart3, TrendingUp, Award, AlertCircle } from "lucide-react";

// Mock data for demonstrations
const modelPerformanceData = [
  { model: "Logistic Regression", AUROC: 0.73, AP: 0.68 },
  { model: "Gradient Boosting", AUROC: 0.71, AP: 0.66 },
  { model: "Ensemble", AUROC: 0.75, AP: 0.70 }
];

const hitsAtKData = [
  { year: 2019, "Top-1": 0.8, "Top-2": 0.6, "Top-3": 0.7 },
  { year: 2020, "Top-1": 0.7, "Top-2": 0.8, "Top-3": 0.8 },
  { year: 2021, "Top-1": 0.9, "Top-2": 0.7, "Top-3": 0.9 },
  { year: 2022, "Top-1": 0.6, "Top-2": 0.9, "Top-3": 0.8 },
  { year: 2023, "Top-1": 0.8, "Top-2": 0.8, "Top-3": 0.9 }
];

const thresholdData = [
  { threshold: 0.1, precision: 0.32, recall: 0.95, f1: 0.48 },
  { threshold: 0.2, precision: 0.41, recall: 0.88, f1: 0.56 },
  { threshold: 0.3, precision: 0.52, recall: 0.79, f1: 0.63 },
  { threshold: 0.4, precision: 0.61, recall: 0.68, f1: 0.64 },
  { threshold: 0.5, precision: 0.68, recall: 0.58, f1: 0.62 },
  { threshold: 0.6, precision: 0.74, recall: 0.47, f1: 0.58 },
  { threshold: 0.7, precision: 0.81, recall: 0.35, f1: 0.49 },
  { threshold: 0.8, precision: 0.87, recall: 0.24, f1: 0.38 },
  { threshold: 0.9, precision: 0.93, recall: 0.12, f1: 0.21 }
];

const COLORS = ['#6366F1', '#14B8A6', '#F59E0B'];

const Visualizations = () => {
  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Model Visualizations</h1>
          <p className="text-muted-foreground">
            Explore model performance metrics, historical trends, and prediction analysis
          </p>
        </div>

        {/* Alert for missing data */}
        <Alert className="mb-8">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Some visualizations are using demo data. In production, these would load from artifacts/cv_metrics.json and cv_predictions.csv.
          </AlertDescription>
        </Alert>

        <div className="grid gap-8">
          {/* Model Performance */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="eurovision-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-primary" />
                  Model AUROC Performance
                </CardTitle>
                <CardDescription>
                  Area Under ROC Curve for each model
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={modelPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="model" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Bar dataKey="AUROC" fill="#6366F1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="eurovision-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5 text-secondary" />
                  Average Precision
                </CardTitle>
                <CardDescription>
                  Precision-Recall Area Under Curve
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={modelPerformanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="model" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Bar dataKey="AP" fill="#14B8A6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Hits@K Trends */}
          <Card className="eurovision-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Hits@K Performance Over Time
              </CardTitle>
              <CardDescription>
                Model accuracy at predicting Top-K finishers by year
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={hitsAtKData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="Top-1" 
                    stroke="#6366F1" 
                    strokeWidth={3}
                    dot={{ fill: "#6366F1", strokeWidth: 2, r: 6 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="Top-2" 
                    stroke="#14B8A6" 
                    strokeWidth={3}
                    dot={{ fill: "#14B8A6", strokeWidth: 2, r: 6 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="Top-3" 
                    stroke="#F59E0B" 
                    strokeWidth={3}
                    dot={{ fill: "#F59E0B", strokeWidth: 2, r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Threshold Explorer */}
          <Card className="eurovision-card">
            <CardHeader>
              <CardTitle>Threshold Explorer</CardTitle>
              <CardDescription>
                Precision, Recall, and F1-Score across different prediction thresholds
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={thresholdData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="threshold" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="precision" 
                    stroke="#6366F1" 
                    strokeWidth={2}
                    name="Precision"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="recall" 
                    stroke="#14B8A6" 
                    strokeWidth={2}
                    name="Recall"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="f1" 
                    stroke="#F59E0B" 
                    strokeWidth={2}
                    name="F1-Score"
                  />
                </LineChart>
              </ResponsiveContainer>
              
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <h4 className="font-semibold mb-2">Optimal Threshold Analysis</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <Badge variant="outline" className="mb-1">Best Precision</Badge>
                    <p>Threshold: 0.9 (93.0%)</p>
                  </div>
                  <div>
                    <Badge variant="outline" className="mb-1">Best Recall</Badge>
                    <p>Threshold: 0.1 (95.0%)</p>
                  </div>
                  <div>
                    <Badge variant="outline" className="mb-1">Best F1</Badge>
                    <p>Threshold: 0.4 (64.0%)</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Model Comparison Summary */}
          <div className="grid md:grid-cols-3 gap-6">
            <Card className="text-center eurovision-card">
              <CardHeader>
                <CardTitle className="text-primary">Best AUROC</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-primary mb-2">75.0%</div>
                <Badge className="bg-primary text-primary-foreground">Ensemble Model</Badge>
              </CardContent>
            </Card>

            <Card className="text-center eurovision-card">
              <CardHeader>
                <CardTitle className="text-secondary">Best AP</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-secondary mb-2">70.0%</div>
                <Badge className="bg-secondary text-secondary-foreground">Ensemble Model</Badge>
              </CardContent>
            </Card>

            <Card className="text-center eurovision-card">
              <CardHeader>
                <CardTitle className="text-accent-foreground">Avg Hits@3</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-accent-foreground mb-2">84.0%</div>
                <Badge variant="outline">2019-2023</Badge>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Visualizations;