using System;
using System.Collections.Generic;
[Serializable]
public class Step
{
    public List<Food> food;
    public List<CollectorAgent> collectors;
    public List<ExplorerAgent> explorers;
    public Storage storage;
    public int max_food;
    public int total_food;
    public int collected_food;
    public int steps_taken;
}