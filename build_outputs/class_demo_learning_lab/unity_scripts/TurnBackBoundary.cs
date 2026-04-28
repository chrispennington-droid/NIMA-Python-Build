using UnityEngine;

// NIMA Phase II Spatial Review Learning Lab - class demo build.
// Attach to a trigger collider that wraps an out-of-MVP boundary. When the
// player enters, they are stopped and either pushed back or teleported to a
// safe return point. This keeps tour participants inside the approved
// learning experience (the lobby, prove-out floor, stairs, landing, overlook).
//
// Recommended setup:
//   - Wrap each MVP_Barrier_* node from the GLB with a slightly larger trigger
//     collider, OR add this script to one of the MVP_Barrier_* nodes after
//     converting its MeshCollider to a trigger.
//   - Set "safeReturnPoint" to a Transform inside the lobby spawn area.
public class TurnBackBoundary : MonoBehaviour
{
    [Tooltip("Tag on the player object. Default = Player.")]
    public string playerTag = "Player";

    [Tooltip("Where to send the player when they enter the boundary.")]
    public Transform safeReturnPoint;

    [Tooltip("If safeReturnPoint is null, push the player back this many meters along the inverse of their forward vector.")]
    public float pushBackMeters = 1.5f;

    [Tooltip("Message shown briefly to the player.")]
    public string message = "This area is outside the current MVP review boundary.";

    [Tooltip("Seconds the message stays on screen.")]
    public float messageSeconds = 3.0f;

    private float msgUntil = 0f;

    private void Reset()
    {
        var col = GetComponent<Collider>();
        if (col != null) col.isTrigger = true;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag(playerTag)) return;

        var cc = other.GetComponent<CharacterController>();
        if (cc != null) cc.enabled = false;

        if (safeReturnPoint != null)
        {
            other.transform.position = safeReturnPoint.position;
            other.transform.rotation = safeReturnPoint.rotation;
        }
        else
        {
            other.transform.position -= other.transform.forward * pushBackMeters;
            other.transform.Rotate(0f, 180f, 0f);
        }

        if (cc != null) cc.enabled = true;
        msgUntil = Time.time + messageSeconds;
        Debug.Log($"[TurnBackBoundary] '{name}' returned the player. {message}");
    }

    private void OnGUI()
    {
        if (Time.time > msgUntil) return;
        var style = new GUIStyle(GUI.skin.box) { fontSize = 16, alignment = TextAnchor.MiddleCenter };
        var rect = new Rect(Screen.width / 2 - 350, 80, 700, 40);
        GUI.Box(rect, message, style);
    }
}
