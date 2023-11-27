using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Collector : Agent
{
    GameObject food;

    new void Awake()
    {
        base.Awake();
        food = transform.FirstOrDefault(x => x.CompareTag("Food")).gameObject;
    }

    public void Step(int x, int y, float time, bool isCarryingFood)
    {
        base.Step(x, y, time);
        food.SetActive(isCarryingFood);
    }
}
