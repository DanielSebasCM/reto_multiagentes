// Root myDeserializedClass = JsonConvert.DeserializeObject<Root>(myJsonResponse);
using System.Collections.Generic;

public class ModelResponse
{
    public int steps { get; set; }
    public List<Step> data { get; set; }
}
