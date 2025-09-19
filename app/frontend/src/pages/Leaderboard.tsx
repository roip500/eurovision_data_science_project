import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Download, Trophy, Medal, Award } from "lucide-react";

// Mock leaderboard data
const mockData2023 = [
  { rank: 1, country: "Sweden", song: "Tattoo", artist: "Loreen", prediction: 0.87, actualPlace: 1, isTopK: true },
  { rank: 2, country: "Finland", song: "Cha Cha Cha", artist: "Käärijä", prediction: 0.82, actualPlace: 2, isTopK: true },
  { rank: 3, country: "Israel", song: "Unicorn", artist: "Noa Kirel", prediction: 0.78, actualPlace: 3, isTopK: true },
  { rank: 4, country: "Italy", song: "Due Vite", artist: "Marco Mengoni", prediction: 0.71, actualPlace: 4, isTopK: false },
  { rank: 5, country: "Norway", song: "Queen of Kings", artist: "Alessandra", prediction: 0.69, actualPlace: 5, isTopK: false },
  { rank: 6, country: "Ukraine", song: "Heart of Steel", artist: "Tvorchi", prediction: 0.65, actualPlace: 6, isTopK: false },
  { rank: 7, country: "Belgium", song: "Because of You", artist: "Gustaph", prediction: 0.61, actualPlace: 8, isTopK: false },
  { rank: 8, country: "Estonia", song: "Bridges", artist: "Alika", prediction: 0.58, actualPlace: 14, isTopK: false },
];

const Leaderboard = () => {
  const [selectedYear, setSelectedYear] = useState("2023");
  const [selectedTopK, setSelectedTopK] = useState("3");
  
  const years = ["2023", "2022", "2021", "2020", "2019"];
  const topKOptions = ["1", "2", "3"];

  const getPositionIcon = (place: number) => {
    if (place === 1) return <Trophy className="h-4 w-4 text-eurovision-gold" />;
    if (place === 2) return <Medal className="h-4 w-4 text-eurovision-silver" />;
    if (place === 3) return <Award className="h-4 w-4 text-eurovision-bronze" />;
    return null;
  };

  const handleDownloadCSV = () => {
    // Mock CSV download
    const csvContent = mockData2023.map(row => 
      `${row.country},${row.song},${row.artist},${row.prediction},${row.actualPlace}`
    ).join('\n');
    
    const blob = new Blob([`Country,Song,Artist,Prediction,ActualPlace\n${csvContent}`], 
      { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `eurovision-leaderboard-${selectedYear}-top${selectedTopK}.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Eurovision Leaderboard</h1>
          <p className="text-muted-foreground">
            Compare predicted probabilities with actual Eurovision results
          </p>
        </div>

        {/* Controls */}
        <Card className="eurovision-card mb-8">
          <CardHeader>
            <CardTitle>Filter Options</CardTitle>
            <CardDescription>
              Select year and Top-K setting to view predictions and results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4 items-end">
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Year</label>
                <Select value={selectedYear} onValueChange={setSelectedYear}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {years.map(year => (
                      <SelectItem key={year} value={year}>{year}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex-1">
                <label className="text-sm font-medium mb-2 block">Top-K</label>
                <Select value={selectedTopK} onValueChange={setSelectedTopK}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {topKOptions.map(k => (
                      <SelectItem key={k} value={k}>Top-{k}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <Button onClick={handleDownloadCSV} variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Download CSV
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Leaderboard Table */}
        <Card className="eurovision-card">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Eurovision {selectedYear} - Top-{selectedTopK} Predictions
              <Badge variant="outline">
                {mockData2023.length} entries
              </Badge>
            </CardTitle>
            <CardDescription>
              Songs ranked by predicted Top-{selectedTopK} probability. 
              <span className="text-primary font-medium"> Highlighted rows</span> indicate true Top-{selectedTopK} finishers.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">Rank</TableHead>
                    <TableHead>Country</TableHead>
                    <TableHead>Song</TableHead>
                    <TableHead>Artist</TableHead>
                    <TableHead className="text-right">Prediction</TableHead>
                    <TableHead className="text-center">Actual Place</TableHead>
                    <TableHead className="text-center">Top-{selectedTopK}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockData2023.map((entry) => {
                    const isTopK = parseInt(selectedTopK) >= entry.actualPlace;
                    return (
                      <TableRow 
                        key={entry.country}
                        className={isTopK ? "bg-primary/5 border-primary/20" : ""}
                      >
                        <TableCell className="font-medium">
                          #{entry.rank}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getPositionIcon(entry.actualPlace)}
                            <span className="font-medium">{entry.country}</span>
                          </div>
                        </TableCell>
                        <TableCell>{entry.song}</TableCell>
                        <TableCell className="text-muted-foreground">{entry.artist}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-2">
                            <div className="w-20 bg-muted rounded-full h-2">
                              <div 
                                className="h-2 rounded-full bg-gradient-to-r from-primary to-secondary"
                                style={{ width: `${entry.prediction * 100}%` }}
                              />
                            </div>
                            <span className="font-mono text-sm w-12 text-right">
                              {(entry.prediction * 100).toFixed(0)}%
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-center">
                          <div className="flex items-center justify-center gap-1">
                            {getPositionIcon(entry.actualPlace)}
                            <span className="font-medium">{entry.actualPlace}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-center">
                          {isTopK ? (
                            <Badge className="bg-primary/10 text-primary border-primary/20">
                              ✓ Yes
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-muted-foreground">
                              No
                            </Badge>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
            
            {/* Summary Stats */}
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-muted/50 rounded-lg">
                <div className="text-2xl font-bold text-primary">3/3</div>
                <div className="text-sm text-muted-foreground">Top-{selectedTopK} Predicted</div>
              </div>
              <div className="text-center p-4 bg-muted/50 rounded-lg">
                <div className="text-2xl font-bold text-secondary">100%</div>
                <div className="text-sm text-muted-foreground">Accuracy</div>
              </div>
              <div className="text-center p-4 bg-muted/50 rounded-lg">
                <div className="text-2xl font-bold text-accent-foreground">0.82</div>
                <div className="text-sm text-muted-foreground">Avg Prediction</div>
              </div>
              <div className="text-center p-4 bg-muted/50 rounded-lg">
                <div className="text-2xl font-bold">26</div>
                <div className="text-sm text-muted-foreground">Total Songs</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Leaderboard;