using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Collector : MonoBehaviour
{
    public int id;
    public int x;
    public int y;
    GameObject food;
    Animator animator;

    void Awake()
    {
        food = transform.FirstOrDefault(x => x.CompareTag("Food")).gameObject;
        animator = GetComponent<Animator>();
    }

    public void Init(int id, int x, int y)
    {
        this.id = id;
        this.x = x;
        this.y = y;
    }

    public void Step(int x, int y, float time, bool isCarryingFood)
    {
                // if not movng play anim sit
        if (this.x == x && this.y == y)
        {
            animator.Play("sit");
        }
        else
        {
            animator.Play("walk");
        }
        this.x = x;
        this.y = y;
        if (isCarryingFood)
            food.SetActive(true);
        else
            food.SetActive(false);

        StartCoroutine(MoveTo(x, y, time));
    }

    IEnumerator MoveTo(int x, int y, float time)
    {
        Vector3 target = new Vector3(x, 0, y);
        Vector3 origin = transform.position;
        Quaternion targetRotation = Quaternion.LookRotation(target - transform.position);
        float elapsedTime = 0;
        while (elapsedTime < time)
        {
            float currTime = elapsedTime / time;
            transform.SetPositionAndRotation(
                Vector3.Lerp(origin, target, currTime),
                Quaternion.Slerp(transform.rotation, targetRotation, currTime));
            elapsedTime += Time.deltaTime;
            yield return null;
        }
        transform.SetPositionAndRotation(target, targetRotation);
    }
}
