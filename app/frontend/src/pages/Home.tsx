import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Target, BarChart3, BookOpen, Sparkles } from "lucide-react";
import heroImage from "@/assets/eurovision-hero.jpg";

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: `url(${heroImage})` }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-primary/90 to-secondary/80" />
        </div>
        
        <div className="relative container mx-auto px-4 py-24 md:py-32">
          <div className="max-w-4xl mx-auto text-center text-white">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Eurovision Top-K Predictor
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-white/90 max-w-2xl mx-auto">
              Predict which Eurovision songs will finish in the Top-K using machine learning models trained on historical data and song features.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/predict">
                <Button size="lg" className="bg-white text-primary hover:bg-white/90 font-semibold px-8">
                  <Target className="mr-2 h-5 w-5" />
                  Start Predicting
                </Button>
              </Link>
              
              <Link to="/about">
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="border-white/80 text-white bg-white/10 hover:bg-white/20 backdrop-blur-sm font-semibold px-8"
                >
                  <BookOpen className="mr-2 h-5 w-5" />
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Explore Eurovision Data Science</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Dive into Eurovision predictions with advanced ML models, interactive visualizations, and comprehensive analysis tools.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Link to="/predict">
              <Card className="eurovision-card hover:shadow-eurovision-lg transition-all duration-300 cursor-pointer group">
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 h-12 w-12 rounded-lg bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Target className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">Smart Predictions</CardTitle>
                  <CardDescription>
                    Enter song features and lyrics to get Top-K probability predictions from multiple ML models
                  </CardDescription>
                </CardHeader>
                <CardContent className="text-center">
                  <div className="flex items-center justify-center space-x-2 text-primary">
                    <Sparkles className="h-4 w-4" />
                    <span className="font-medium">Try It Now</span>
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link to="/visualizations">
              <Card className="eurovision-card hover:shadow-eurovision-lg transition-all duration-300 cursor-pointer group">
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 h-12 w-12 rounded-lg bg-gradient-to-br from-secondary to-secondary/80 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <BarChart3 className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">Data Visualizations</CardTitle>
                  <CardDescription>
                    Explore model performance metrics, historical trends, and interactive charts
                  </CardDescription>
                </CardHeader>
                <CardContent className="text-center">
                  <div className="flex items-center justify-center space-x-2 text-secondary">
                    <BarChart3 className="h-4 w-4" />
                    <span className="font-medium">View Charts</span>
                  </div>
                </CardContent>
              </Card>
            </Link>

            <Link to="/about">
              <Card className="eurovision-card hover:shadow-eurovision-lg transition-all duration-300 cursor-pointer group">
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 h-12 w-12 rounded-lg bg-gradient-to-br from-accent-foreground to-accent-foreground/80 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <BookOpen className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle className="text-xl">Methodology</CardTitle>
                  <CardDescription>
                    Learn about our models, features, cross-validation, and ethical considerations
                  </CardDescription>
                </CardHeader>
                <CardContent className="text-center">
                  <div className="flex items-center justify-center space-x-2 text-accent-foreground">
                    <BookOpen className="h-4 w-4" />
                    <span className="font-medium">Read More</span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Try a Quick Demo</h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            See the predictor in action with a pre-filled Eurovision song example
          </p>
          
          <Link to="/predict?demo=true">
            <Button size="lg" className="font-semibold px-8">
              <Sparkles className="mr-2 h-5 w-5" />
              Load Demo Song
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;