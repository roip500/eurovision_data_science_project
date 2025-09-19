import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, Database, Brain, Shield, Target } from "lucide-react";

const About = () => {
  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-4">Methodology</h1>
          <p className="text-xl text-muted-foreground">
            A comprehensive overview of our Eurovision Top-K prediction methodology
          </p>
        </div>

        <div className="space-y-8">
          {/* Dataset */}
          <Card className="eurovision-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-6 w-6 text-primary" />
                Dataset Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p className="text-muted-foreground mb-4">
                Our Eurovision prediction system is built on a comprehensive dataset spanning multiple years of Eurovision contests.
              </p>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">Data Sources</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li>• Official Eurovision results and rankings</li>
                    <li>• Song metadata (year, country, language, broadcaster)</li>
                    <li>• Performance characteristics (BPM, running order, dancers)</li>
                    <li>• Complete song lyrics for text analysis</li>
                    <li>• Historical country performance data</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Data Quality</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li>• Cleaned and validated entries</li>
                    <li>• Missing value imputation strategies</li>
                    <li>• Outlier detection and handling</li>
                    <li>• Cross-year consistency checks</li>
                    <li>• Standardized feature encoding</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Feature Engineering */}
          <Card className="eurovision-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-6 w-6 text-secondary" />
                Feature Engineering
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <h4 className="font-semibold mb-3 text-primary">Temporal Features</h4>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li><Badge variant="outline" className="mr-2">Year-within</Badge>Normalized features by year</li>
                    <li><Badge variant="outline" className="mr-2">Country history</Badge>Historical performance metrics</li>
                    <li><Badge variant="outline" className="mr-2">Trend analysis</Badge>Multi-year performance trends</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-3 text-secondary">Performance Features</h4>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li><Badge variant="outline" className="mr-2">BPM norm</Badge>Z-score normalized tempo</li>
                    <li><Badge variant="outline" className="mr-2">Running order</Badge>Position effects analysis</li>
                    <li><Badge variant="outline" className="mr-2">Stage elements</Badge>Dancers, props, staging</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-3 text-accent-foreground">Text Features</h4>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li><Badge variant="outline" className="mr-2">TF-IDF</Badge>Term frequency analysis</li>
                    <li><Badge variant="outline" className="mr-2">N-grams</Badge>1-3 gram patterns</li>
                    <li><Badge variant="outline" className="mr-2">Lyrics stats</Badge>Length, complexity metrics</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Models */}
          <Card className="eurovision-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-6 w-6 text-primary" />
                Machine Learning Models
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold text-primary mb-2">Logistic Regression (Text + Tabular)</h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      Linear model combining TF-IDF text features with engineered tabular features.
                    </p>
                    <div className="flex flex-wrap gap-1">
                      <Badge variant="outline">L2 regularization</Badge>
                      <Badge variant="outline">Feature scaling</Badge>
                      <Badge variant="outline">Interpretable</Badge>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-secondary mb-2">Histogram Gradient Boosting (Tabular)</h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      Tree-based ensemble model focusing on tabular features with automatic handling of categorical variables.
                    </p>
                    <div className="flex flex-wrap gap-1">
                      <Badge variant="outline">Gradient boosting</Badge>
                      <Badge variant="outline">Feature importance</Badge>
                      <Badge variant="outline">Robust</Badge>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-accent-foreground mb-2">Ensemble Model</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    Simple mean ensemble combining predictions from both models to leverage their complementary strengths.
                  </p>
                  
                  <div className="bg-muted/50 p-4 rounded-lg">
                    <h5 className="font-medium mb-2">Model Performance</h5>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <div className="font-medium">AUROC</div>
                        <div className="text-muted-foreground">0.750</div>
                      </div>
                      <div>
                        <div className="font-medium">Average Precision</div>
                        <div className="text-muted-foreground">0.698</div>
                      </div>
                      <div>
                        <div className="font-medium">Hits@3</div>
                        <div className="text-muted-foreground">84.0%</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Validation */}
          <Card className="eurovision-card">
            <CardHeader>
              <CardTitle>Cross-Validation Strategy</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">GroupKFold by Year</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    We use GroupKFold cross-validation with years as groups to prevent data leakage and ensure temporal validity.
                  </p>
                  
                  <div className="space-y-2 text-sm">
                    <div><Badge variant="outline" className="mr-2">Temporal splits</Badge>Prevents future information leakage</div>
                    <div><Badge variant="outline" className="mr-2">5-fold CV</Badge>Robust performance estimation</div>
                    <div><Badge variant="outline" className="mr-2">Stratified</Badge>Maintains class balance</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-3">Evaluation Metrics</h4>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li><strong>AUROC:</strong> Area Under ROC Curve for ranking quality</li>
                    <li><strong>Average Precision:</strong> Precision-Recall AUC for imbalanced data</li>
                    <li><strong>Hits@K:</strong> Accuracy at predicting top-K finishers</li>
                    <li><strong>Calibration:</strong> Reliability of probability estimates</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Ethics */}
          <Card className="eurovision-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-6 w-6 text-secondary" />
                Ethical Considerations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Bias and Fairness</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    Our models avoid using sensitive demographic attributes and focus on musical and performance characteristics.
                  </p>
                  <div className="grid md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <strong className="text-green-600">What we include:</strong>
                      <ul className="mt-1 space-y-1 text-muted-foreground">
                        <li>• Musical features (BPM, tone, lyrics)</li>
                        <li>• Performance characteristics</li>
                        <li>• Historical contest context</li>
                      </ul>
                    </div>
                    <div>
                      <strong className="text-red-600">What we exclude:</strong>
                      <ul className="mt-1 space-y-1 text-muted-foreground">
                        <li>• Artist demographics</li>
                        <li>• Political or sensitive attributes</li>
                        <li>• Potentially discriminatory features</li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Limitations and Disclaimers</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li>• Predictions are probabilistic estimates, not guarantees</li>
                    <li>• Models reflect historical patterns and may not capture future changes</li>
                    <li>• Eurovision voting involves complex cultural and political factors</li>
                    <li>• Results should be interpreted as research tools, not definitive predictions</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Technical Implementation */}
          <Card className="eurovision-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-6 w-6 text-accent-foreground" />
                Technical Implementation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">Frontend Stack</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li>• React + TypeScript for type safety</li>
                    <li>• Vite for fast development and building</li>
                    <li>• Tailwind CSS for responsive design</li>
                    <li>• Recharts for interactive visualizations</li>
                    <li>• Shadcn/ui for consistent components</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-3">Backend & ML</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li>• Python FastAPI for REST endpoints</li>
                    <li>• scikit-learn for ML pipelines</li>
                    <li>• Joblib for model serialization</li>
                    <li>• Pandas for data manipulation</li>
                    <li>• Cross-validation and evaluation metrics</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default About;