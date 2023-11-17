using System.Collections.Generic;

public class Step
{
    public List<Food> food { get; set; }
    public List<CollectorAgent> collectors { get; set; }
    public List<ExplorerAgent> explorers { get; set; }
    public Storage storage { get; set; }
    public int max_food { get; set; }
    public int total_food { get; set; }
    public int collected_food { get; set; }
    public int steps_taken { get; set; }
}