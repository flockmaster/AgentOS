/* Main JavaScript - Scroll Engine (T-005) */
(function initScrollEngine() {
  console.log("[ScrollEngine] Script Loaded");

  if (typeof lucide !== "undefined" && typeof lucide.createIcons === "function") {
    lucide.createIcons();
    console.log("[ScrollEngine] Icons Initialized");
  }

  const sections = Array.from(document.querySelectorAll("section[id]"));
  const navLinks = Array.from(document.querySelectorAll('.nav-links a[href^="#"]'));
  console.log("[ScrollEngine] DOM Ready", {
    sectionCount: sections.length,
    navLinkCount: navLinks.length,
  });

  if (!sections.length) {
    console.log("[ScrollEngine] No Sections Found, Abort");
    return;
  }

  let activeSectionId = "";
  const visibleRatios = new Map();

  function applyActiveState(sectionId) {
    if (!sectionId) {
      return;
    }
    if (sectionId === activeSectionId) {
      return;
    }

    activeSectionId = sectionId;

    sections.forEach((section) => {
      section.classList.toggle("active", section.id === sectionId);
    });

    navLinks.forEach((link) => {
      const targetId = link.getAttribute("href")?.slice(1) || "";
      link.classList.toggle("active", targetId === sectionId);
    });

    console.log("[ScrollEngine] Active Updated", { sectionId });
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const id = entry.target.id;
        if (!id) {
          return;
        }

        if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
          visibleRatios.set(id, entry.intersectionRatio);
          console.log("[ScrollEngine] Section >=50%", {
            sectionId: id,
            ratio: Number(entry.intersectionRatio.toFixed(3)),
          });
        } else {
          visibleRatios.delete(id);
          console.log("[ScrollEngine] Section <50% or Out", {
            sectionId: id,
            ratio: Number(entry.intersectionRatio.toFixed(3)),
          });
        }
      });

      let candidateId = "";
      let maxRatio = 0;

      visibleRatios.forEach((ratio, id) => {
        if (ratio > maxRatio) {
          maxRatio = ratio;
          candidateId = id;
        }
      });

      if (candidateId) {
        applyActiveState(candidateId);
      }
    },
    {
      threshold: [0, 0.5, 0.75, 1],
    },
  );

  sections.forEach((section) => {
    observer.observe(section);
    console.log("[ScrollEngine] Observing Section", { sectionId: section.id });
  });
  console.log("[ScrollEngine] Observer Started");

  navLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      const targetId = link.getAttribute("href")?.slice(1);
      console.log("[ScrollEngine] Nav Clicked", { targetId: targetId || null });

      if (!targetId) {
        console.log("[ScrollEngine] Invalid TargetId");
        return;
      }

      const targetSection = document.getElementById(targetId);
      if (!targetSection) {
        console.log("[ScrollEngine] Target Section Not Found", { targetId });
        return;
      }

      event.preventDefault();
      targetSection.scrollIntoView({ behavior: "smooth", block: "start" });
      history.pushState(null, "", `#${targetId}`);
      console.log("[ScrollEngine] Smooth Scroll Triggered", { targetId });
      applyActiveState(targetId);
    });
  });
  console.log("[ScrollEngine] Nav Events Bound");

  const initialIdFromHash = window.location.hash.replace("#", "");
  const initialId = initialIdFromHash || sections[0].id;
  if (initialId) {
    console.log("[ScrollEngine] Initial Active Resolve", { initialId });
    applyActiveState(initialId);
  }
})();
