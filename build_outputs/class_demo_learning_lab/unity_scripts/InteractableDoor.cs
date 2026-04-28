using UnityEngine;

// NIMA Phase II Spatial Review Learning Lab - class demo build (optional).
// Lightweight "press E to open" door behavior. Pairs with DoorTransition: use
// DoorTransition for the actual scene change/teleport, and use this on the
// visible door panel if you want a swing animation when E is pressed.
//
// Recommended setup:
//   - Place this on the GLB node "Door_Lobby_To_ProveOut_Level1" or
//     "Door_Level2_To_ProveOut_Overlook".
//   - Add a child trigger collider (the doorway opening) and put DoorTransition
//     on the trigger; this script reacts to the same key.
public class InteractableDoor : MonoBehaviour
{
    [Tooltip("Tag on the player object. Default = Player.")]
    public string playerTag = "Player";

    [Tooltip("Distance (meters) at which the door becomes interactable.")]
    public float interactRadiusMeters = 2.5f;

    public KeyCode openKey = KeyCode.E;

    [Tooltip("Open angle in degrees around the world Y axis.")]
    public float openAngleDeg = 90f;

    [Tooltip("Open/close speed in degrees per second.")]
    public float openSpeedDegPerSec = 180f;

    public bool startsOpen = false;

    private float currentAngle = 0f;
    private float targetAngle = 0f;
    private Quaternion closedRot;
    private Transform player;

    private void Start()
    {
        closedRot = transform.localRotation;
        if (startsOpen) targetAngle = openAngleDeg;
        var p = GameObject.FindGameObjectWithTag(playerTag);
        if (p != null) player = p.transform;
    }

    private void Update()
    {
        if (player == null)
        {
            var p = GameObject.FindGameObjectWithTag(playerTag);
            if (p != null) player = p.transform;
        }

        bool inRange = player != null &&
                       Vector3.Distance(player.position, transform.position) <= interactRadiusMeters;

        if (inRange && Input.GetKeyDown(openKey))
        {
            targetAngle = (Mathf.Abs(targetAngle) > 0.5f) ? 0f : openAngleDeg;
        }

        currentAngle = Mathf.MoveTowards(currentAngle, targetAngle,
                                         openSpeedDegPerSec * Time.deltaTime);
        transform.localRotation = closedRot * Quaternion.Euler(0f, currentAngle, 0f);
    }
}
